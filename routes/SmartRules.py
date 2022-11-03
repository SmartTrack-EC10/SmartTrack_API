import requests, json, traceback
from Logs.log import LogClass

class SmartRules():
    strHttp: str = "http://52.7.63.69:1026"
    jsonHeaders = { "Content-Type": "application/json", "fiware-service": "helixiot", "fiware-servicepath": "/" }

    def CheckWorkedHours(self, request) -> int:
        """Check all rules about workedHours"""

        nReturn = 500 #by default, code response is 500
        try: 
            nReturn = self.__CheckMaintencance__(request)
        except Exception as e:
            LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")

        return nReturn

    def CheckBattery(self, request) -> int:
        """Check all rules is called"""

        nReturn = 500 #by default, code response is 500
        try: 
            objReq = self.__GetRequestBody__(request)
            nReturn = self.__UpdateBattery__(objReq)
        except Exception as e:
            LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")

        return nReturn

    def __CalcBatteryPerc(self, voltage: float) -> float:
        """Voltage to percentage"""
        maximum = 8.6
        minimum = 5.3
        return round((voltage - minimum) * 100 / (maximum - minimum), 0)

    def __UpdateBattery__(self, objRequest: object) -> int:
        """Update on Broker the Battery percentage"""
        batteryVolt = objRequest["object"]["battery"]
        batteryPerc = self.__CalcBatteryPerc(batteryVolt)
        strID = objRequest["object"]["id"]

        strRoute = self.strHttp + "/v2/entities/" + strID + "/attrs"
        objReturn = {"batteryPerc": { "value": batteryPerc, "type": "Number"}}  

        if(batteryPerc < 25):
            objReturn["ledStatus"] = {"value": "lowBattery", "type": "Text"}
        elif(batteryPerc > 25 and objRequest["object"]["ledStatus"] == "lowBattery"):
            objReturn["ledStatus"] = {"value": "ativo", "type": "Text"}

        return self.__SendDefaultRequest__("POST", strRoute, objReturn, self.jsonHeaders)    

    def __GetRequestBody__(self, request) -> object:
        """Get request's body to json object"""
        response = request.get_data()
        return json.loads(response.decode("utf-8"))

    def __UpdateWorkedHours__(self, request) -> object:
        """Update WorkedHours on Object"""
        jsonObject = self.__GetRequestBody__(request)
        nLastWorkedHours = jsonObject["object"]["lastWorkedHours"]
        jsonObject["object"]["workedHours"] += nLastWorkedHours 

        return jsonObject

    def __CheckEachOneMaintenance__(self, objReturn: object, objRules: object, nWorkedHours: int, nHours: int, strKey: str) -> object:
        """Rule Maintenance"""

        nCount = int(nWorkedHours / nHours)
        if  (nCount > objRules[strKey]): 
            nDiff = nCount - objRules[strKey]
            objReturn[strKey] = {"value": nCount, "type": "Number"}            
            objReturn["activeNow"] = {"value": objReturn["activeNow"]["value"] + nDiff, "type": "Number"}
            strLastQuantity = strKey.replace("all", "lastQuantity")
            objReturn[strLastQuantity] =  { "value": nDiff, "type": "Number" }
            
        return objReturn

    def __CheckLedStatusRule__(self, objReturn: object) -> object:
        """Rule Led Status"""

        if  (objReturn["activeNow"]["value"] > 0): 
            objReturn["ledStatus"] = {"value": "manutencao", "type": "Text"}
            
        return objReturn

    def __CheckRuleMaintenance__(self, nWorkedHours: int, objRules: object) -> object:
        """"Check Rules' Maintenance"""
        objReturn = {}
        objReturn["activeNow"] = {"value": objRules["activeNow"], "type": "Number"}
        objReturn["workedHours"] = {"value": nWorkedHours, "type": "Number"}

        # 10 Hours' rule
        objReturn = self.__CheckEachOneMaintenance__(objReturn, objRules, nWorkedHours, 10, "allTrigged10Hours")
        # 50 Hours' rule
        objReturn = self.__CheckEachOneMaintenance__(objReturn, objRules, nWorkedHours, 50, "allTrigged50Hours")
        # 250 Hours' rule
        objReturn = self.__CheckEachOneMaintenance__(objReturn, objRules, nWorkedHours, 250, "allTrigged250Hours")
        # 500 Hours' rule
        objReturn = self.__CheckEachOneMaintenance__(objReturn, objRules, nWorkedHours, 500, "allTrigged500Hours")
        # 1000 Hours' rule
        objReturn = self.__CheckEachOneMaintenance__(objReturn, objRules, nWorkedHours, 1000, "allTrigged1000Hours")

        # Set led status
        objReturn = self.__CheckLedStatusRule__(objReturn)

        return objReturn

    def __CheckMaintencance__(self, request) -> int:
        """Check for some Maintenance Rule"""

        jsonObject = self.__UpdateWorkedHours__(request)
        strID = jsonObject["object"]["id"]
        nWorkedHours = jsonObject["object"]["workedHours"]
        objRules = jsonObject["object"]["rules"]

        objRules = self.__CheckRuleMaintenance__(nWorkedHours, objRules)

        strRoute = self.strHttp + "/v2/entities/" + strID + "/attrs"

        return self.__SendDefaultRequest__("POST", strRoute, objRules, self.jsonHeaders)


    def __SendDefaultRequest__(self, strType: str, strRoute: str, jsonPayload: object, jsonHeaders: object) -> int: 
        """Send Request and return response code"""
        objResponse = None
        command = strType.upper()

        if(command == "POST"):
            objResponse = requests.post(url=strRoute, json = jsonPayload, headers = jsonHeaders)
            self.__LogRequest__(objResponse, jsonPayload)

            return objResponse.status_code
        elif(command == "PUT"):
            objResponse = requests.put(url=strRoute, json = jsonPayload, headers = jsonHeaders)
            self.__LogRequest__(objResponse, jsonPayload)

            return objResponse.status_code
        else:
            return 500

    def __LogRequest__(self, objResponse: object, objSent: object) -> None:
        """Log Resquest information"""

        if(objResponse.ok):
            LogClass().Info("{ \"Info\": \"request has succeeded\", \"StatusCode\": " + str(objResponse.status_code) + 
                ", \"object\": {" + str(objSent) + "} }")
        else:
            LogClass().Error("{ \"Error\": \"Some error happen\", \"StatusCode\": " + str(objResponse.status_code) + 
                ", \"Message\": \"" + objResponse.text +  "\", \"object\": {" + str(objSent) + "} }")