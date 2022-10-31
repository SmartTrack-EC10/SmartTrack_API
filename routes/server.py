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

@appServer.route("/rules/workedHours", methods=['POST'])
def WorkedHours_POST():
    """file: ../swagger/rules/workedHours/post_workedHours.yml"""
    nCode = 500
    nCode = smartRulesReq.CheckWorkedHours(request)
    return __SendResponseDefault__(nCode, lsMessageResponse, True if nCode == 400 else False)

@appServer.route("/rules/battery", methods=['POST'])
def Battery_POST():
    """file: ../swagger/rules/battery/post_battery.yml"""
    nCode = 500
    nCode = smartRulesReq.CheckBattery(request)
    return __SendResponseDefault__(nCode, lsMessageResponse, True if nCode == 400 else False)

@appServer.route("/notifications", methods=['PUT'])
def Notifications_PUT():
    """file: ../swagger/notifications/put_notifications.yml"""
    nCode = 500
    lsMessageResponse = []
    nCode = notifications.UpdateNotifications(request, lsMessageResponse)
    return __SendResponseDefault__(nCode, lsMessageResponse, True if nCode == 400 else False)

@appServer.route("/notifications", methods=['POST'])
def Notifications_POST():
    """file: ../swagger/notifications/post_notifications.yml"""
    nCode = 500
    lsMessageResponse = []
    nCode = notifications.CreateNotifications(request, lsMessageResponse)
    return __SendResponseDefault__(nCode, lsMessageResponse, True if nCode == 400 else False)

@appServer.route("/notifications", methods=['GET'])
def Notifications_GET():
    """file: ../swagger/notifications/get_notifications.yml"""
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