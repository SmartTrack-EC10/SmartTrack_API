import json, traceback
from math import fabs
from urllib.parse import urlparse

from Logs.log import LogClass
from Email.email import SMTP_Email
from database.ConnectDB import ConnectionDB

class Notifications():  
    mongoDB: ConnectionDB
    notificationsEmail = SMTP_Email()

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
            lsMessageResponse.append("header type is not allowed!")

        return bReturn

    def __CheckObjectNotification__(self, objNotification: str, lsMessageResponse: list) -> bool:
        """Check if Truck object there are all necessaries fields"""
        #Check main field to save on Notifications
        if("message" in objNotification and "object" in objNotification and "email" in objNotification and "datetime" in objNotification):
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
        strQuery = urlparse(request.path).query

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

    def __GetCollectionHeaders__(self, request) -> str:
        """Get header from request"""
        strCollection = request.headers.get("type")
        if strCollection is not None:
            strCollection = strCollection.upper()

        return strCollection

    def __GetRequestBody__(self, request) -> object:
        """Get request's body to json object"""

        content_len = int(request.headers.get("Content-Length"), 0)
        raw_body = request.rfile.read(content_len)

        return json.loads(raw_body)

    def __CheckBodyRequest__(self, objDocument: object, lsMessageResponse: list) -> bool:
        """Check required fields on object"""
        bValid = True

        if("emails" not in objDocument or len(objDocument["emails"]) == 0):
            lsMessageResponse.append("email not in request")
            bValid = False
        elif("object" not in objDocument):
            lsMessageResponse.append("email not in request")
            bValid = False

        return bValid

    def CreateNotifications(self, request, lsMessageResponse: list) -> int:
        """Python HTTP Server that handles Notifications"""
        try:            
            strCollection = self.__GetCollectionHeaders__(request)
            if(strCollection is None):
                strError = "Invalid collection!"
                LogClass().Error(strError)
                lsMessageResponse.append(strError)
                return 400

            objDocument = self.__GetRequestBody__(request)
            if(not self.__CheckBodyRequest__(objDocument, lsMessageResponse)):
                return 400

            objDocument["status"] = "active" #implement status as active

            response = self.__SaveNotification__("NOTIFICATIONS", strCollection, objDocument, lsMessageResponse)

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

    def __SaveNotification__(self, strDatabase: str, strCollection: str, objNotification: object, lsMessageResponse: list) -> bool:
        """Save a notification on Database"""
        if(self.__CheckAll__(strDatabase, strCollection, lsMessageResponse)
            and self.__CheckObjectNotification__(objNotification, lsMessageResponse)):            
            return self.mongoDB.SaveObject(strCollection, objNotification)
        else:  
            return False
   