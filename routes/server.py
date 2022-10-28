from flask import Blueprint, Response, request, redirect
from flasgger import swag_from

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
    """file: ../swagger/rules/rules.yml"""
    nCode = 500
    lsMessageResponse = []
    nCode = smartRulesReq.CheckSmartRules(request)
    __SendResponseDefault__(nCode, lsMessageResponse, True if nCode == 400 else False)

@appServer.route("/notifications", methods=['POST'])
def Notifications_POST():
    """file: ../swagger/notifications/notifications.yml"""
    nCode = 500
    lsMessageResponse = []
    nCode = notifications.CreateNotifications(request, lsMessageResponse)
    __SendResponseDefault__(nCode, lsMessageResponse, True if nCode == 400 else False)

@appServer.route("/notifications", methods=['GET'])
def Notifications_GET():
    nCode = 500
    lsMessageResponse = []

    nCode = notifications.GetNotifications(request, lsMessageResponse)
    return __SendResponseDefault__(nCode, lsMessageResponse, True if nCode == 400 else False)

@appServer.route("/history", methods=['GET'])
def History_GET():
    """file: ../swagger/history/history.yml"""
    nCode = 500
    lsMessageResponse = []

    nCode = historyDB.GetHistory(request, lsMessageResponse)
    return __SendResponseDefault__(nCode, lsMessageResponse, True if nCode == 400 else False)

def __SendResponseDefault__(nCode: int, lsMessageResponse: list = None, bSaveError: bool = False) -> None:
        """Python HTTP Server that handles responses to requests"""
        resp = Response(status=nCode)

        if(lsMessageResponse is not None):
            resp.headers["Content-type"] = "application/json"
            resp.data = bytes(''.join(lsMessageResponse), "utf-8")

        if(bSaveError):
            LogClass().Error(''.join(lsMessageResponse)) 

        return resp