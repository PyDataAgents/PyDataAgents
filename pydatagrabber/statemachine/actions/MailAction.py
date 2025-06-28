from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from ..StatemachineException import StatemachineException
from ..Action import Action


@dataclass
class MailAction(Action):
    
    smtp_server : str = field(default=None, metadata={"description": "host of the mail server to use"})
    port : int = field(default=None, metadata={"description": "port of the smtp server"})
    mail_account : str = field(default=None, metadata={"description": "mail account to use for login"})
    pw : str = field(default=None, metadata={"description": "password of the mail server"})
    recipient : str = field(default=None, metadata={"description": "mail address of the recipient"})
    subject : str = field(default=None,  metadata={"description": "subject of the mail"})
    body : str = field(default=None,  metadata={"description": "body of the mail"})
    
    def __init__(self):
        super().__init__()
        
    def execute(self):
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = self.subject if self.subject else "Do Not Reply - Mail from " + self.cname()
        message["From"] = self.mail_account
        message["To"] = self.recipient
        
        mt = MIMEText(self.body, "html")
        
        message.attach(mt)
        
        # Send
        try:
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()  # Secure the connection
                server.login(self.mail_account, self.pw)
                server.sendmail(self.mail_account, self.recipient, message.as_string())
                #print("✅ Email sent successfully.")
        except Exception as e:
            raise StatemachineException("could not send mail from " + self.cname()) from e