from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse
from routes.Notifications import Notifications
from Email.email import SMTP_Email
from Logs.log import LogClass

import json, traceback


class PythonServer(SimpleHTTPRequestHandler):
    notificationsDB = Notifications()
    notificationsEmail = SMTP_Email()

    def do_POST(self):
        """Python HTTP Server that handles POST requests"""

        if(self.path.upper() == "/NOTIFICATIONS"):
            self.__CreateNotifications__()
        else:
            self.__SendResponseDefault__(400, "{ \"Error\": \"Bad Request: Path not found!\" }")

    def do_GET(self):
        """Python HTTP Server that handles GET requests"""
        strPath = self.path.split('?')[0]

        if(strPath.upper() == "/NOTIFICATIONS"):
            self.__GetNotifications__()
        elif(strPath.upper() == "/HISTORY"):                 
            self.__SendResponseDefault__(400, "{ \"Error\": \"Not implemented yet!\" }")
        else:     
            self.__SendResponseDefault__(400, "{ \"Error\": \"Bad Request: Path not found!\" }")

    def do_PUT(self):
        """Python HTTP Server that handles PUT requests"""

        if(self.path.upper() == "/NOTIFICATIONS"):
            self.__SendResponseDefault__(400, "{ \"Error\": \"Not implemented yet!\" }")
        else:     
            self.__SendResponseDefault__(400, "{ \"Error\": \"Bad Request: Path not found!\" }")

    def __SendResponseDefault__(self, nCode: int, strInfo: str, strMessage: str = None, bSaveError: bool = False):
        """Python HTTP Server that handles responses to requests"""
        self.send_response(nCode, strInfo)
        self.end_headers()

        if(strMessage is not None):
            self.send_header("Content-type", "application/json")
            self.wfile.write(bytes(strMessage, "utf-8"))

        if(bSaveError):
            LogClass().Error(strMessage)
    
        self.connection.close()

    def __GetCollectionHeaders__(self) -> str:
        strCollection = self.headers.get("type")
        if strCollection is not None:
            strCollection = strCollection.upper()

        return strCollection

    def __CreateNotifications__(self) -> None:
        """Python HTTP Server that handles Notifications"""
        try:
            content_len = int(self.headers.get("Content-Length"), 0)
            raw_body = self.rfile.read(content_len)
            
            strCollection = self.__GetCollectionHeaders__()
            if(strCollection is None):
                strError = "{ \"Error\": \"Invalid collection!\" }"
                LogClass().Error(strError)
                self.SendResponseDefault(400, "Bad Request", strError)
                return None

            objDocument = json.loads(raw_body)
            strMessageResponse: str = ""
            response = self.notificationsDB.SaveNotification(strCollection, objDocument, strMessageResponse)

            if(response):
                self.__SendResponseDefault__(200, "OK")
                self.notificationsEmail.SendEmail(objDocument)
                LogClass().Info("{ \"Info\": \"Notification saved successfully\" }")
            else:
                LogClass().Error(strMessageResponse)
                self.__SendResponseDefault__(400, "", strMessageResponse, True)   
        except json.JSONDecodeError as e:
            LogClass().Error("{ \"Error\": \"" + str(traceback.format_exc()) + "\" }")
            self.__SendResponseDefault__(400, "Bad Request", str(e))                   
        except Exception as e:
            LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")
            self.__SendResponseDefault__(500, "Internal Error", str(e))

    def __GetParameters__(self) -> list:
        """Create Query to send to Database"""
        strQuery = urlparse(self.path).query
        objParameters = dict(qc.split("=") for qc in strQuery.split("&"))
        
        return objParameters

    def __GetNotifications__(self) -> None:
        """Get Notifications on DataBase"""
        try:
            objParameters = self.__GetParameters__()

            strCollection = str(objParameters['type']).upper()
            if(strCollection is None):
                self.SendResponseDefault(400, "Bad Request", "{ \"Error\": \"Parameter 'type' is missing!\" }")
                return None            
           
            strMessageResponse:str = None
            response = self.notificationsDB.GetNotification(strCollection, objParameters, strMessageResponse)(strCollection, strParameters, strMessageResponse)

            if(response):
                LogClass().Info("{ \"Info\": \"Notification saved successfully\" }")
                self.__SendResponseDefault__(200, "OK")
                self.notificationsEmail.SendEmail(objDocument)                
            else:
                LogClass().Error(strMessageResponse)
                self.__SendResponseDefault__(400, "", strMessageResponse, True)                    
        except Exception as e:
            LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")
            self.__SendResponseDefault__(500, "Internal Error", "{ \"Exception\": \"" + str(e) + "\" }")