from http.server import SimpleHTTPRequestHandler
from routes.Notifications import Notifications
from Email.email import SMTP_Email
import json

class PythonServer(SimpleHTTPRequestHandler):
    notificationsDB = Notifications()
    notificationsEmail = SMTP_Email()

    def do_POST(self):  
        """Python HTTP Server that handles POST requests"""
        if(self.path.upper() == "/NOTIFICATIONS"):
            self.CreateNotifications()
        else:
            self.SendResponseDefault(400, "Bad Request: Path not found!")

    def do_GET(self):
        """Python HTTP Server that handles GET requests"""
        self.SendResponseDefault(400, "Bad Request: Method not implemented yet!")

    def SendResponseDefault(self, code: int, info: str, message: str = None):
        """Python HTTP Server that handles responses to requests"""
        self.send_response(code, info)
        self.end_headers()

        if(message is not None):
            self.send_header("Content-type", "application/json")
            self.wfile.write(bytes('{ "Error": "{message}" }', "utf-8"))
    
        self.connection.close()

    def GetCollection(self) -> str:
        strCollection = self.headers.get("type")
        if strCollection is not None:
            strCollection = strCollection.upper()

        return strCollection

    def CreateNotifications(self) -> None:
        """Python HTTP Server that handles Notifications"""
        try:
            content_len = int(self.headers.get("Content-Length"), 0)
            raw_body = self.rfile.read(content_len)
            
            strCollection = self.GetCollection()
            if(strCollection is None):
                self.SendResponseDefault(400, "Bad Request", "{ \"Error\": \"Invalid collection!\" }")
                return None

            objDocument = json.loads(raw_body)
            strMessageResponse:str = None
            response = self.notificationsDB.SaveNotification(strCollection, objDocument, strMessageResponse)

            if(response):
                self.SendResponseDefault(200, "OK")
                self.notificationsEmail.SendEmail(objDocument)
            else:
                self.SendResponseDefault(400, "", strMessageResponse)                    
        except Exception as e:
            self.SendResponseDefault(500, "Internal Error", str(e))

