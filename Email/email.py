import smtplib, ssl, os, traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text  import MIMEText
from email.mime.image import MIMEImage

from Email.templateEmail import SMTP_Template
from Logs.log import LogClass

class SMTP_Email():
    port: int 
    server: str 
    sender_user: str
    sender_pass: str 
    context: ssl.SSLContext
    msgRoot: MIMEMultipart
    msgAlternative: MIMEMultipart

    def __init__(self):
        self.port = 465 #For SSL
        self.server = "smtp.gmail.com" #os.environ.get("SMTP_Server")
        self.sender_user = "smarttrack.notifications@gmail.com" #os.environ.get("SMTP_User")
        self.sender_pass = "wtiagxvwnxmyrniz" #os.environ.get("SMTP_Pass")

        # Create a multipart message and set headers
        self.msgRoot = MIMEMultipart('related')
        self.msgAlternative = MIMEMultipart('alternative')
        self.msgRoot.attach(self.msgAlternative)        

        # Create a secure SSL context
        self.context = ssl.create_default_context()

    def __MIMEMultipart__(self, subject: str, receiver: str) -> None:
        """Update the Addressee Email"""        
        self.msgRoot['From'] = self.sender_user
        self.msgRoot['Subject'] = subject
        self.msgRoot['To'] = receiver
        self.msgRoot.preamble = 'This is a multi-part message in MIME format.'

    def SendEmail(self, objNotification: object) -> None:
        """Send email to specific person"""
        try:
            receivers = self.__GetReceiversUsers__()
            if(len(receivers) != 0 and objNotification is not None):

                server = smtplib.SMTP_SSL(self.server, self.port, context=self.context)
                server.login(self.sender_user, self.sender_pass) #sender login

                # Encapsulate the plain and HTML versions of the message body in an
                # 'alternative' part, so message agents can decide which they want to display.                    
                msgText = MIMEText('This is the alternative plain text message.')
                self.msgAlternative.attach(msgText)

                template = SMTP_Template().TemplateHTML(objNotification)  
                self.msgAlternative.attach(MIMEText(template, "html"))

                # This example assumes the image is in the current directory
                try:
                    fp_icon = open('Email\\images\\error.png', 'rb') if True else open('Email\\images\\warning.png', 'rb')
                    msgIconImage = MIMEImage(fp_icon.read()) 
                    msgIconImage.add_header('Content-ID', '<iconMessage>') # Define the image's ID as referenced above

                    fp_logo = open('Email\\images\\logoSmartTrack_1.png', 'rb')
                    msgLogoImage = MIMEImage(fp_logo.read())                         
                    msgLogoImage.add_header('Content-ID', '<iconLogo>')

                    self.msgRoot.attach(msgIconImage)
                    self.msgRoot.attach(msgLogoImage)                      
                except Exception as e:
                    LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")
                finally:
                    fp_icon.close() 
                    fp_logo.close()   

                for rec in receivers:  #send for all
                    self.__MIMEMultipart__(subject = "The First Email by Python!", receiver = rec)
                    server.sendmail(self.sender_user, rec, self.msgRoot.as_string()) 

                LogClass().Info("{ \"Info\": \"Emails sent successfully\" }")

        except Exception as e:
            LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")
        finally:
            server.quit()

    def __GetReceiversUsers__(self) -> list:
        """Get all User's Email to send"""
        return ["081180021@faculdade.cefsa.edu.br"]

    