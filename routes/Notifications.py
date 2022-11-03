import json, traceback
from math import fabs
from urllib.parse import urlparse

from Logs.log import LogClass
from Email.email import SMTP_Email
from database.ConnectDB import ConnectionDB

class Notifications():  
    mongoDB: ConnectionDB
    notificationsEmail = SMTP_Email()

    strHttp: str = "http://52.7.63.69:1026"
    jsonHeaders = { "Content-Type": "application/json", "fiware-service": "helixiot", "fiware-servicepath": "/" }

    def __init__(self):
        """Constructor to Notifications"""
        self.mongoDB = ConnectionDB()

    def __CheckConnection__(self, strDatabase: str, strCollection: str, lsMessageResponse: list) -> bool:
        """Start Connections to MongoDB"""
        if(self.mongoDB.StartDataBase(strDatabase, strCollection)):
            return True
        else:
            lsMessageResponse.append("Colection: {strCollection} can\'t be created!")
            return False

    def __CheckCollections__(self, strCollection: str, lsMessageResponse: list) -> bool:
        """Check Collections that are accepted by Notifications"""
        switch = { "TRUCK": True, "PERSON": True, "AGRIFARM": True, "AGRIPARCEL": True }

        bReturn = switch.get(strCollection, False)

        if not bReturn:
            lsMessageResponse.append("Type is not allowed!")

        return bReturn

    def __CheckObjectNotification__(self, objNotification: str, lsMessageResponse: list) -> bool:
        """Check if Truck object there are all necessaries fields"""
        #Check main field to save on Notifications
        if("message" in objNotification and "object" in objNotification and "email" in objNotification):
            return True
        else:
            lsMessageResponse.append("Object is invalid, check all fields!")
            return False

    def __CheckAll__(self, strDatabase: str, strCollection: str, lsMessageResponse: list) -> bool:
        """Check all requirements to access DataBase"""
        if(self.__CheckCollections__(strCollection, lsMessageResponse)
        and self.__CheckConnection__(strDatabase, strCollection, lsMessageResponse)):
            return True
        else:
            return False 

    def __GetParameters__(self, request, lsMessageResponse: list):
        """Create Query to send to Database"""
        strQuery = urlparse(request.full_path).query

        if(len(strQuery) == 0):
            lsMessageResponse.append("Bad Request: None parameters found!")
            return []

        objParameters = dict(qc.split("=") for qc in strQuery.split("&"))

        return objParameters

    def __GetNotifications__(self, strDatabase: str, strCollection: str, objParameters: object, lsMessageResponse: list) -> list:
        if(self.__CheckConnection__(strDatabase, strCollection, lsMessageResponse)):
            return self.mongoDB.GetObject(strCollection, objParameters)
        else:  
            return []

    def GetNotifications(self, request, lsMessageResponse: list) -> int:
        """Get Notifications on DataBase"""
        try:
            objParameters = self.__GetParameters__(request, lsMessageResponse)

            if(len(lsMessageResponse) != 0):
                return 400

            strCollection = str(objParameters['type']).upper()
            if(strCollection is None):
                lsMessageResponse.append("Parameter 'type' is missing!")                
                return 400

            objParameters["id"] = objParameters["id"].replace("%3A", ":")
            
            lsMessageResponse.append(self.__GetNotifications__("NOTIFICATIONS", strCollection, objParameters, lsMessageResponse))

            if(lsMessageResponse):
                LogClass().Info("{ \"Info\": \"Notifications requested successfully\" }")
                return 200                             
            else:
                LogClass().Error(lsMessageResponse)
                return 400                    
        except Exception as e:
            LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")
            lsMessageResponse.append(str(e))
            return 500 
    
    def __GetRequestBody__(self, request) -> object:
        """Get request's body to json object"""
        response = request.get_data()
        return json.loads(response.decode("utf-8"))

    def __CheckBodyRequestCreate__(self, objDocument: object, lsMessageResponse: list) -> bool:
        """Check required fields on object"""
        bValid = True

        if("message" not in objDocument or len(objDocument["message"]) == 0):
            lsMessageResponse.append("message not in request")
            bValid = False
        elif("id" not in objDocument or len(objDocument["id"]) == 0):
            lsMessageResponse.append("id not in request")
            bValid = False
        elif("type" not in objDocument or len(objDocument["type"]) == 0):
            lsMessageResponse.append("type not in request")
            bValid = False
        elif("email" not in objDocument or len(objDocument["email"]) == 0):
            lsMessageResponse.append("email not in request")
            bValid = False
        elif("object" not in objDocument):
            lsMessageResponse.append("object not in request")
            bValid = False

        return bValid

    def __SaveNotification__(self, strDatabase: str, strCollection: str, objNotification: object, lsMessageResponse: list) -> bool:
        """Save a notification on Database"""
        if(self.__CheckAll__(strDatabase, strCollection, lsMessageResponse)
            and self.__CheckObjectNotification__(objNotification, lsMessageResponse)):            
            return self.mongoDB.SaveObject(strCollection, objNotification)
        else:  
            return False

    def __UpdateStatusLedGeofence__(self, objDocument: object) -> int:
        """Update Status led on Enter/Leaving geofence"""
        nCode = 204
        strLedStatus = objDocument["object"]["ledStatus"]
        strRule = objDocument["rule"]

        if(strRuleobjDocument["object"]["ledStatus"] != "lowBattery"):
            strID = objDocument["id"]
            strRoute = self.strHttp + "/v2/entities/" + strID + "/attrs"

            objSend = {"ledStatus": {"value": "outGeofence", "type": "Text"}}
            nCode = self.__SendDefaultRequest__("POST", strRoute, objReturn, self.jsonHeaders)          

        return nCode

    def CreateNotifications(self, request, lsMessageResponse: list) -> int:
        """Python HTTP Server that handles Notifications"""
        try:            
            strCollection = "" 
            objDocument = self.__GetRequestBody__(request)
            if(objDocument["type"] is None):
                strError = "Invalid type!"
                LogClass().Error(strError)
                lsMessageResponse.append(strError)
                return 400
            else:
                strCollection = objDocument["type"].upper()

            if(not self.__CheckBodyRequestCreate__(objDocument, lsMessageResponse)):
                return 400

            objDocument["status"] = "active" #implement status as active
            response = self.__SaveNotification__("NOTIFICATIONS", strCollection, objDocument, lsMessageResponse)

            if(response and self.__UpdateStatusLedGeofence__(objDocument) == 204):
                LogClass().Info("{ \"Info\": \"Notification saved successfully\" }")
                self.notificationsEmail.SendEmail(objDocument)
                return 200              
            else:
                return 400   
        except json.JSONDecodeError as e:
            LogClass().Error("{ \"Error\": \"" + str(traceback.format_exc()) + "\" }")
            lsMessageResponse.append(str(traceback.format_exc()))
            return 400           
        except Exception as e:
            LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")
            lsMessageResponse.append(str(e))
            return 500   

    def __CheckBodyRequestUpdate__(self, objDocument: object, lsMessageResponse: list) -> bool:
        """Check required fields on object"""
        bValid = True
        eStatus = ["active", "unactive"]

        if("id" not in objDocument or len(objDocument["id"]) == 0):
            lsMessageResponse.append("id not in request")
            bValid = False
        elif("type" not in objDocument or len(objDocument["type"]) == 0):
            lsMessageResponse.append("type not in request")
            bValid = False        
        elif("status" not in objDocument or eStatus.index(objDocument["status"]) == 0):
            lsMessageResponse.append("status is not valid")
            bValid = False

        return bValid

    def __UpdateNotification__(self, strDatabase: str, strCollection: str, id: str, objReq: object, lsMessageResponse: list) -> bool:
        """Save a notification on Database"""
        if(self.__CheckAll__(strDatabase, strCollection, lsMessageResponse)):
            return self.mongoDB.UpdateObject(strCollection, id, objReq)
        else:  
            return False

    def UpdateNotifications(self, request, lsMessageResponse: list) -> int:
        """Update status from Notification"""
        try:            
            objDocument = self.__GetRequestBody__(request)
            if(not self.__CheckBodyRequestUpdate__(objDocument, lsMessageResponse)):
                return 400

            strCollection = objDocument["type"]

            objId = objDocument["id"]
            objReq["status"] = objDocument["status"]

            response = self.__UpdateNotification__("NOTIFICATIONS", strCollection, objId, objDocument, lsMessageResponse)

            if(response):
                LogClass().Info("{ \"Info\": \"Notification saved successfully\" }")
                self.notificationsEmail.SendEmail(objDocument)
                return 200              
            else:
                return 400   
        except json.JSONDecodeError as e:
            LogClass().Error("{ \"Error\": \"" + str(traceback.format_exc()) + "\" }")
            lsMessageResponse.append(str(traceback.format_exc()))
            return 400           
        except Exception as e:
            LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")
            lsMessageResponse.append(str(e))
            return 500 

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