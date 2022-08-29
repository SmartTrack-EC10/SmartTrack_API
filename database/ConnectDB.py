from pymongo import MongoClient, database, collection
from Logs.log import LogClass

import traceback

class ConnectionDB():
    CLIENT: database.Database
    clNotification: collection.Collection

    def __init__(self):
        self.CLIENT = None
        self.clNotification = None

    def __ConnectionDataBase__(self, strCollection: str)-> bool:
        """Create a Connection to MongoDB"""
        try:
            self.CLIENT = MongoClient("mongodb://localhost:27017/")
            if "NOTIFICATIONS" not in self.CLIENT.list_database_names():
                self.clNotification = self.CLIENT["NOTIFICATIONS"].create_collection(name= strCollection)
                self.clNotification.insert_one({})
                return True
            else:
                self.clNotification = self.CLIENT.get_database(name="NOTIFICATIONS")
                if strCollection in self.clNotification.list_collection_names():
                    self.clNotification.get_collection(strCollection)
                    return True
                else:
                    self.clNotification.create_collection(strCollection)
                    self.clNotification.insert_one({})
                    return True
        except Exception as e:
            LogClass().Critical("{ \"Message\": \"Connection to MongoDB is not working!\", \"Exception\": \"" + 
                str(traceback.format_exc()) + "\" }")
            return False

    def StartDataBase(self, strCollection: str) -> bool:
        """Start Database"""
        try:
            if(self.__ConnectionDataBase__(strCollection) and self.clNotification is not None):
                LogClass().Info("{ \"Info\": \"DataBase started as successfull!\" }")
                return True
        except Exception as e:
            LogClass().Critical("{ \"Message\": \"" + "Some error happen on creating collection: {strCollection}\", \"Exception\": \"" + 
                str(traceback.format_exc()) + "\" }")
            return False

        return False 

    def SaveObject(self, strCollection: str, objNotification: object) -> collection.Collection:
        """Save a object on Database"""
        try:
            if(self.CLIENT is not None and self.clNotification is not None):
                objResp = self.clNotification.get_collection(strCollection).insert_one(objNotification)

                if(objResp.acknowledged):
                    LogClass().Info("{ \"Info\": \"Notification created with id: " + str(objResp.inserted_id) + "\" }")
                else:
                    objResp._raise_if_unacknowledged(Exception)

                return objResp.acknowledged
            else:
                return None
        except Exception as e:
            LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")        

    def GetObject(self, strCollection: str, lsQuery: list) -> collection.Collection:
        """Get a List of Objects on Database"""
        if(self.CLIENT is not None and self.clNotification is not None):
            objResp = self.clNotification.get_collection(strCollection).find(filter=objNotification)           

            return self.clNotification.get_collection(strCollection).find(objNotification)
        else:
            return None



