from pymongo import MongoClient, database, collection

class ConnectionDB():
    CLIENT: database.Database
    clNotification: collection.Collection

    def __init__(self):
        self.CLIENT = None
        self.clNotification = None

    def __ConnectionDataBase__(self, strCollection):
        """Create a Connection to MongoDB"""
        try:
            self.CLIENT = MongoClient("mongodb://localhost:27017/")
            if "notifications" not in self.CLIENT.list_database_names():
                self.clNotification = self.CLIENT["notifications"].create_collection(name= strCollection)
                self.clNotification.insert_one({})
            else:
                self.clNotification = self.CLIENT.get_database(name="notifications")
                
                if strCollection in self.clNotification.list_collections():
                    self.clNotification.get_collection(strCollection)
                else:
                    self.clNotification.create_collection(strCollection)
                    self.clNotification.insert_one({})

        except Exception(e):
            print("Connection to MongoDB is not working! \nException: " + e) 

    def StartDataBase(self, strCollection) -> bool:
        try:
            if(self.__ConnectionDataBase__(strCollection) and self.clNotification is not None):
                print("DataBase started as successfull!")
                return True
        except Exception(e):
            print("Some error happen on creating collection: {strCollection}, see logs!")
            return False

        return False 

    def GetDatabase(self, strCollection) -> collection.Collection:
        if(self.CLIENT is not None and self.clNotification is not None):
            return self.clNotification
        else:
            return None



