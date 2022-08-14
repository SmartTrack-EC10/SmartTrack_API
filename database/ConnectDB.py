from pymongo import MongoClient, database, collection

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
            print("Connection to MongoDB is not working! \n\rException: " + str(e)) 
            return False

    def StartDataBase(self, strCollection: str) -> bool:
        try:
            if(self.__ConnectionDataBase__(strCollection) and self.clNotification is not None):
                print("DataBase started as successfull!")
                return True
        except Exception as e:
            print("Some error happen on creating collection: {strCollection}, \n\rException: " + str(e))
            return False

        return False 

    def SaveObject(self, strCollection: str, objNotification: object) -> collection.Collection:
        if(self.CLIENT is not None and self.clNotification is not None):
            return self.clNotification.get_collection(strCollection).insert_one(objNotification).acknowledged
        else:
            return None



