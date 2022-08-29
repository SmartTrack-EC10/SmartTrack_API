from database.ConnectDB import ConnectionDB

class Notifications():  
    mongoDB: ConnectionDB

    def __init__(self):
        """Constructor to Notifications"""
        self.mongoDB = ConnectionDB()

    def __CheckConnection__(self, strCollection: str, strMessageResponse: str) -> bool:
        """Start Connections to MongoDB"""
        if(self.mongoDB.StartDataBase(strCollection)):
            return True
        else:
            strMessageResponse =  "{ \"Error\": " + "\"Colection: {strCollection} can\'t be created!\"" + " }"
            return False

    def __CheckCollections__(self, strCollection: str, strMessageResponse: str) -> bool:
        """Check Collections that are accepted by Notifications"""
        switch = { "TRUCK": True, "PERSON": True, "AGRIFARM": True, "AGRIPARCEL": True }

        bReturn = switch.get(strCollection, False)

        if not bReturn:
            strMessageResponse = "{ \"Error\": \"header type is not allowed\" }"

        return bReturn

    def __CheckObjectNotification__(self, objNotification: str, strMessageResponse: str) -> bool:
        """Check if Truck object there are all necessaries fields"""
        #Check main field to save on Notifications
        if("message" in objNotification and "id" in objNotification and "type" in objNotification):
            return True
        else:
            strMessageResponse = "{ \"Error\": \"Object is invalid, check all fields! \" }"
            return False

    def __CheckAll__(self, strCollection: str, strMessageResponse: str) -> bool:
        """Check all requirements to access DataBase"""
        if(self.__CheckCollections__(strCollection, strMessageResponse)
        and self.__CheckConnection__(strCollection, strMessageResponse)):
            return True
        else:
            return False       

    def SaveNotification(self, strCollection: str, objNotification: object, strMessageResponse: str) -> bool:
        """Save a notification on Database"""
        if(self.__CheckAll__(strCollection, strMessageResponse)
            and self.__CheckObjectNotification__(objNotification, strMessageResponse)):            
            return self.mongoDB.SaveObject(strCollection, objNotification)
        else:  
            return False

    def GetNotification(self, strCollection: str, lsQuery: list, strMessageResponse: str) -> bool:
        if(self.__CheckAll__(strCollection, lsQuery, strMessageResponse)):            
            return self.mongoDB.GetObject(strCollection, lsQuery)
        else:  
            return False