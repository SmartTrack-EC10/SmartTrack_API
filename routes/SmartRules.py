import requests, json, traceback
from Logs.log import LogClass

class SmartRules():
    strHttp: str = "http://52.7.63.69:1026"
    jsonHeaders = { "Content-Type": "application/json", "fiware-service": "helixiot", "fiware-servicepath": "/" }
      
    def CheckSmartRules(self, request) -> int:
        """Check all rules is called"""

        nReturn = 500 #by default, code response is 500
        try:        
            strType = request.headers.get("type")

            if(strType == "lastWorkedHours"):
                nReturn = self.__UpdateWorkedHours__(request)
            elif(strType == "workedHours"):
                nReturn = self.__CheckMaintencance__(request)
            else:
                return nReturn

        except Exception as e:
            LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")

        return nReturn

    def __GetRequestBody__(self, request) -> object:
        """Get request's body to json object"""

        content_len = int(request.headers.get("Content-Length"), 0)
        raw_body = request.rfile.read(content_len)

        return json.loads(raw_body)

    def __UpdateWorkedHours__(self, request) -> int:
        """Update Worked Hours on Context Broker"""

        jsonObject = self.__GetRequestBody__(request)
        strID = jsonObject["object"]["id"]
        nValue = jsonObject["object"]["lastWorkedHours"]

        strRoute = self.strHttp + "/v2/entities/" + strID + "/attrs/workedHours"
        jsonPayload = { "value": { "$inc": nValue }, "type": "Number" }

        return self.__SendDefaultRequest__("PUT", strRoute, jsonPayload, self.jsonHeaders)

    def __CheckEachOneMaintenance__(self, objRules: object, nWorkedHours: int, nHours: int, strKey: str) -> object:
        """"Rule Maintenance"""

        nCount = int(nWorkedHours / nHours)
        if  (nCount > objRules[strKey]): 
            objRules[strKey] = {"value": nCount, "type": "Number"}
            objRules["activeNow"] = {"value": objRules["activeNow"] + 1, "type": "Number"}
        else:
            del objRules[strKey]
            
        return objRules

    def __CheckRuleMaintenance__(self, nWorkedHours: int, objRules: object) -> object:
        """"Check Rules' Maintenance"""

        # 10 Hours' rule
        objRules = self.__CheckEachOneMaintenance__(objRules, nWorkedHours, 10, "allTrigged10Hours")
        # 50 Hours' rule
        objRules = self.__CheckEachOneMaintenance__(objRules, nWorkedHours, 50, "allTrigged50Hours")
        # 250 Hours' rule
        objRules = self.__CheckEachOneMaintenance__(objRules, nWorkedHours, 250, "allTrigged250Hours")
        # 500 Hours' rule
        objRules = self.__CheckEachOneMaintenance__(objRules, nWorkedHours, 500, "allTrigged500Hours")
        # 1000 Hours' rule
        objRules = self.__CheckEachOneMaintenance__(objRules, nWorkedHours, 1000, "allTrigged1000Hours")

        return objRules

    def __CheckMaintencance__(self, request) -> int:
        """Check for some Maintenance Rule"""

        jsonObject = self.__GetRequestBody__(request)
        strID = jsonObject["object"]["id"]
        nWorkedHours = jsonObject["object"]["workedHours"]
        objRules = jsonObject["object"]

        objRules = self.__CheckRuleMaintenance__(nWorkedHours, objRules)

        strRoute = self.strHttp + "/v2/entities/" + strID + "/attrs"

        return self.__SendDefaultRequest__("POST", strRoute, objRules, self.jsonHeaders)


    def __SendDefaultRequest__(self, strType: str, strRoute: str, jsonPayload: object, jsonHeaders: object) -> int: 
        """Send Request and return response code"""
        objResponse = None
        command = strType.upper()

        if(command == "POST"):
            objResponse = requests.post(url=strRoute, json = jsonPayload, headers = jsonHeaders)
            self.__LogRequest__(objResponse)

            return objResponse.status_code
        elif(command == "PUT"):
            objResponse = requests.put(url=strRoute, json = jsonPayload, headers = jsonHeaders)
            self.__LogRequest__(objResponse)

            return objResponse.status_code
        else:
            return 500

    def __LogRequest__(self, objResponse) -> None:
        """Log Resquest information"""

        if(objResponse.ok):
            LogClass().Info("{ \"Info\": \"request has succeeded\", \"StatusCode\": " + str(objResponse.status_code) + " }")
        else:
            LogClass().Error("{ \"Error\": \"Some error happen\", \"StatusCode\": " + str(objResponse.status_code) + 
                ", \"Message\": " + objResponse.text + " }")