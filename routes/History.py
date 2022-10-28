import traceback
from urllib.parse import urlparse
from Logs.log import LogClass
from dateutil import parser
from database.ConnectDB import ConnectionDB


class History():
    """Get the persistent data on database"""
    mongoDB: ConnectionDB

    def __init__(self):
        """Constructor to History"""
        self.mongoDB = ConnectionDB()

    def __CheckConnection__(self, strCollection: str, lsMessageResponse: list) -> bool:
        """Start Connections to MongoDB"""
        strDatabase = "sth_helixiot"

        if(self.mongoDB.StartDataBase(strDatabase, strCollection)):
            return True
        else:
            lsMessageResponse.append("{ \"Error\": " + "\"Colection: " + strCollection + " can\'t be found!\"" + " }")
            return False

    def __GetParameters__(self, request, lsMessageResponse: list):
        """Create Query to send to Database"""
        strQuery = urlparse(request.full_path).query

        if(len(strQuery) == 0):
            lsMessageResponse.append("{ \"Error\": \"Bad Request: None parameters found!\" }")
            return []

        objParameters = dict(qc.split("=") for qc in strQuery.split("&"))

        # normalize swagger test
        objParameters["id"] = objParameters["id"].replace("%3A", ":")
        objParameters["dateStart"] = objParameters["dateStart"].replace("%3A", ":")
        objParameters["dateEnd"] = objParameters["dateEnd"].replace("%3A", ":")

        return objParameters

    def __CheckParameters__(self, objParameters: object, lsMessageResponse: list)-> bool():
        """Create Query to send to Database"""
        error = []
        if("type" not in objParameters):
            error.append("type not found")
        if("id" not in objParameters):
            error.append("id not found")
        if("field" not in objParameters):
            error.append("field not found")
        if("dateStart" not in objParameters):
            error.append("dateStart not found")
        if("dateEnd" not in objParameters):
            error.append("dateEnd not found")

        if(len(error) != 0):
            lsMessageResponse.append("{ \"Error\": " + str(error) + " }")
        
        return True if len(lsMessageResponse) != 0 else False

    def __SetObjectParameters__(self, objParameters: object) -> object:
        """Set the parameters to query"""
        objRequestParameter = {}

        objRequestParameter["attrName"] = objParameters["field"]    
        objRequestParameter["recvTime"] = {
            "$gte": parser.parse(objParameters["dateStart"]), 
            "$lt":  parser.parse(objParameters["dateEnd"  ])
        }    
        return objRequestParameter

    def __GetHistoryDB__(self, strCollection: str, objParameters: object, lsMessageResponse: list) -> list:
        """Check connection and make request"""
        if(self.__CheckConnection__(strCollection, lsMessageResponse)):
            return self.mongoDB.GetObject(strCollection, objParameters)
        else:  
            return []    

    def GetHistory(self, request, lsMessageResponse: list) -> int:         
        try:
            objParameters = self.__GetParameters__(request, lsMessageResponse)
            if(self.__CheckParameters__(objParameters, lsMessageResponse)):
                return 400
            
            strCollection = "sth_/_" + objParameters["id"] + "_" + objParameters["type"]
            objQuery = self.__SetObjectParameters__(objParameters)

            lsMessageResponse.append(self.__GetHistoryDB__(strCollection, objQuery, lsMessageResponse))

            if(len(lsMessageResponse) != 0):
                LogClass().Info("{ \"Info\": \"History requested successfully\" }")
                return 200                   
            else:
                LogClass().Error(lsMessageResponse)
                return 400                    
        except Exception as e:
            LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")
            lsMessageResponse.append("{ \"Exception\": \"" + str(e) + "\" }")
            return 500 