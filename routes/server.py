import traceback
from flask import Blueprint, request, redirect, url_for

from Logs.log import LogClass
from routes.Notifications import Notifications
from routes.SmartRules import SmartRules
from routes.History import History

"""SmartTrack API"""
notifications = Notifications()
smartRulesReq = SmartRules()
historyDB = History()

appServer = Blueprint("", __name__)

@appServer.route("/")
def apidocs():
    return redirect("/apidocs")

@appServer.route("/rules", methods=['POST'])
def Rules_POST():
    nCode = 500
    lsMessageResponse = []
    nCode = smartRulesReq.CheckSmartRules(request)
    __SendResponseDefault__(nCode, "", lsMessageResponse, True if nCode == 400 else False)

@appServer.route("/notifications", methods=['POST'])
def Notifications_POST():
    nCode = 500
    lsMessageResponse = []
    nCode = self.notifications.CreateNotifications(request, lsMessageResponse)
    self.__SendResponseDefault__(nCode, "", lsMessageResponse, True if nCode == 400 else False)

@appServer.route("/notifications", methods=['GET'])
def Notifications_GET():
    nCode = 500
    lsMessageResponse = []

    nCode = notifications.CreateNotifications(request, lsMessageResponse)
    __SendResponseDefault__(nCode, "", lsMessageResponse, True if nCode == 400 else False)

def __SendResponseDefault__(nCode: int, strInfo: str, lsMessageResponse: list = None, bSaveError: bool = False):
        """Python HTTP Server that handles responses to requests"""
        self.send_response(nCode, strInfo)

        if(lsMessageResponse is not None):   
            self.send_header("Content-type", "application/json")    
            self.end_headers()         
            self.wfile.write(bytes(''.join(lsMessageResponse), "utf-8"))

        if(bSaveError):
            LogClass().Error(''.join(lsMessageResponse))    
        
        self.connection.close()

class PythonServer():    
    """SmartTrack API"""
    notifications = Notifications()
    smartRulesReq = SmartRules()
    historyDB = History()
    
    def do_POST(self):
        """Python HTTP Server that handles POST requests"""
        nCode = 500
        lsMessageResponse = []

        if(self.path.upper() == "/NOTIFICATIONS"):
            nCode = self.notifications.CreateNotifications(self, lsMessageResponse)
        elif(self.path.upper() == "/RULES"):
            nCode = self.smartRulesReq.CheckSmartRules(self)
        else:
            self.__SendResponseDefault__(400, "{ \"Error\": \"Bad Request: Path not found!\" }")
        
        self.__SendResponseDefault__(nCode, "", lsMessageResponse, True if nCode == 400 else False)

    def do_GET(self):
        """Python HTTP Server that handles GET requests"""
        nCode = 500
        lsMessageResponse = []

        if(self.path.upper() == "/NOTIFICATIONS"):
            nCode = self.notifications.GetNotifications(self, lsMessageResponse)           
        elif(self.path.upper() == "/HISTORY"):    
            nCode = self.historyDB.GetHistory(self, lsMessageResponse)
        else:     
            self.__SendResponseDefault__(400, "", "{ \"Error\": \"Bad Request: Path not found!\" }", True) 

        self.__SendResponseDefault__(nCode, "", lsMessageResponse, True if nCode == 400 else False)       

    def do_PUT(self):
        """Python HTTP Server that handles PUT requests"""
        lsMessageResponse = []

        if(self.path.upper() == "/NOTIFICATIONS"):
            self.__SendResponseDefault__(400, "", "{ \"Error\": \"Not implemented yet!\" }", True)
        else:     
            self.__SendResponseDefault__(400, "", "{ \"Error\": \"Bad Request: Path not found!\" }", True)

    def __SendResponseDefault__(self, nCode: int, strInfo: str, lsMessageResponse: list = None, bSaveError: bool = False):
        """Python HTTP Server that handles responses to requests"""
        self.send_response(nCode, strInfo)

        if(lsMessageResponse is not None):   
            self.send_header("Content-type", "application/json")    
            self.end_headers()         
            self.wfile.write(bytes(''.join(lsMessageResponse), "utf-8"))

        if(bSaveError):
            LogClass().Error(''.join(lsMessageResponse))    
        
        self.connection.close()