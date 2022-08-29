import logging, traceback
from datetime import datetime

class LogClass():
    def __SaveMessage__(self, strType: str, strMessage: str) -> None:
        """Save a message to log File"""
        try:
            strDate = datetime.now().strftime("%d-%m-%Y")
            file = './Logs/'+ strDate + ".txt"

            logging.basicConfig(filename = file, level=logging.INFO, format="[%(asctime)s] - [%(levelname)s] - %(message)s")

            if(strType == "INFO"): logging.info(strMessage)
            elif(strType == "WARN"): logging.warning(strMessage)
            elif(strType == "ERROR"): logging.error(strMessage)
            elif(strType == "CRITICAL"): logging.critical(strMessage)

        except Exception as e:
            logging.basicConfig(filename = "./Logs/LogException.txt", level=logging.CRITICAL, format="[%(asctime)s] - %(name)s - [%(levelname)s] - %(message)s")
            logging.critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")
        finally:
             logging.shutdown()        
    
    def Info(self, strMessage: str) -> None:
        """Create a Info Message to log"""
        self.__SaveMessage__("INFO", strMessage)       

    def Warn(self, strMessage: str) -> None:
        """Create a Warning Message to log"""
        self.__SaveMessage__("WARN", strMessage)

    def Error(self, strMessage: str) -> None:
        """Create a Error Message to log"""
        self.__SaveMessage__("ERROR", strMessage)

    def Critical(self, strMessage: str) -> None:
        """Create a Critical Message to log"""
        self.__SaveMessage__("CRITICAL", strMessage)