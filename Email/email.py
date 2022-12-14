import smtplib, ssl, traceback, os
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
        self.server = os.environ.get("SMTP_Server")
        self.sender_user = os.environ.get("SMTP_User")
        self.sender_pass = os.environ.get("SMTP_Pass")

        # Create a multipart message and set headers
        self.msgRoot = MIMEMultipart('related')
        self.msgAlternative = MIMEMultipart('alternative')
        self.msgRoot.attach(self.msgAlternative)        

        # Create a secure SSL context
        self.context = ssl.create_default_context()

    def __GetReceiversUsers__(self, objNotification) -> list:
        """Get all User's Email to send"""

        if("email" in objNotification or len(objNotification.email) == 0):
            lsEmails =  []

            for email in objNotification['email']:
                lsEmails.append(email)

            return lsEmails
        else:
            LogClass().Error("No email has been setted.")

        return []

    def __MIMEMultipart__(self, subject: str, receiver: str) -> None:
        """Update the Addressee Email"""        
        self.msgRoot['From'] = self.sender_user
        self.msgRoot['Subject'] = subject
        self.msgRoot['To'] = receiver
        self.msgRoot.preamble = 'This is a multi-part message in MIME format.'

    def SendEmail(self, objNotification: object) -> None:
        """Send email to specific person"""
        server = smtplib.SMTP_SSL(self.server, self.port, context=self.context)
        server.login(self.sender_user, self.sender_pass) #sender login

        try:
            receivers = self.__GetReceiversUsers__(objNotification)
            if(len(receivers) != 0 and objNotification is not None):
                # Encapsulate the plain and HTML versions of the message body in an
                # 'alternative' part, so message agents can decide which they want to display.                    
                msgText = MIMEText('This is the alternative plain text message.')
                self.msgAlternative.attach(msgText)

                template = SMTP_Template().TemplateHTML(objNotification)  
                self.msgAlternative.attach(MIMEText(template, "html"))

                # This example assumes the image is in the current directory
                try:
                    fp_icon = open('/home/ubuntu/SmartTrack API/Email/images/error.png', 'rb')
                    msgIconImage = MIMEImage(fp_icon.read()) 
                    msgIconImage.add_header('Content-ID', '<iconMessage>') # Define the image's ID as referenced above

                    fp_logo = open('/home/ubuntu/SmartTrack API/Email/images/logoSmartTrack_1.png', 'rb')
                    msgLogoImage = MIMEImage(fp_logo.read())                         
                    msgLogoImage.add_header('Content-ID', '<iconLogo>')

                    self.msgRoot.attach(msgIconImage)
                    self.msgRoot.attach(msgLogoImage)                      
                except Exception as e:
                    LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")
                finally:
                    fp_icon.close() 
                    fp_logo.close()  

                qtda = objNotification["qtda"]

                for rec in receivers:  #send for all
                    for qt in range(qtda):
                        self.__MIMEMultipart__(subject = "SmartTrack - Notification", receiver = rec)
                        server.sendmail(self.sender_user, rec, self.msgRoot.as_string()) 

                LogClass().Info("{ \"Info\": \"Emails sent successfully\" }")

        except Exception as e:
            LogClass().Critical("{ \"Exception\": \"" + str(traceback.format_exc()) + "\" }")
        finally:
            server.quit()
    