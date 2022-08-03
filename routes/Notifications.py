from database.ConnectDB import ConnectionDB

class Notifications():  
    mongoDB: ConnectionDB

    def __init__(self):
        """Constructor to Notifications"""
        self.mongoDB = None

    def __CheckConnection__(strCollection) -> bool:
        """Start Connections to MongoDB"""
        if(self.mongoDB.StartDataBase(strCollection)):
            return True
        else:
            return False

    def __CheckCollections__(self, strCollection: str, strMessageResponse: str) -> bool:
        """Check Collections that are accepted by Notifications"""
        switch = { "TRUCK": True, "PERSON": True, "AGRIFARM": True, "AGRIPARCEL": True }

        bReturn = switch.get(strCollection, False)

        if not bReturn:
            strMessageResponse = "{ \"Error\": \"header type is not allowed\" }"

        return bReturn

    def __CheckObjectNotificationTruck__(self, objNotification: str, strMessageResponse: str) -> bool:
        """Check if object that are all necessaries fields"""
        if objNotification["type"].upper() != "TRUCK":
            strMessageResponse = "Object to validation incorrect!"
            return False

        return ("message" in objNotification and "id" in objNotification and "type" in objNotification 
        and "TimeInstant" in objNotification and "battery" in objNotification and "dataTruck" in objNotification 
        and "fuel" in objNotification and "greenLight_status" in objNotification and "lastMaintenance" in objNotification 
        and "location" in objNotification and "motionDetection" in objNotification and "motorTemperature" in objNotification
        and "ownedBy" in objNotification and "redLight_status" in objNotification and "workedHours" in objNotification
        and "yellowLight_status" in objNotification)

    def __CheckAll__(self, strCollection: str, objNotification: object, strMessageResponse: str) -> bool:
        return (self.__CheckCollections__(strCollection, strMessageResponse) 
        and self.__CheckObjectNotification__(objNotification, strMessageResponse) 
        and self.__CheckConnection__(strCollection, strMessageResponse))

    def SaveNotification(self, strCollection: str, objNotification: object, strMessageResponse: str) -> bool:
        if(self.__CheckAll__(strCollection, objNotification, strMessageResponse)):
            print(strCollection)
            print(objNotification)
            return True
        else:  
            return False