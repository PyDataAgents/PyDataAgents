from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from ..StatemachineException import StatemachineException
from ..Action import Action


@dataclass
class MailAction(Action):
    
    smtp_server : str = field(init=True, default=None, metadata={"description": "host of the mail server to use"})
    port : int = field(init=True, default=None, metadata={"description": "port of the smtp server"})
    mail_account : str = field(init=True, default=None, metadata={"description": "mail account to use for login"})
    pw : str = field(init=True, default=None, metadata={"description": "password of the mail server"})
    recipients : list[str] = field(init=True, default_factory=list[str], metadata={"description": "mail address of the recipient"})
    subject : str = field(init=True, default=None,  metadata={"description": "subject of the mail"})
    body : str = field(init=True, default=None,  metadata={"description": "body of the mail"})
    tls : bool = field(init=True, default=True, metadata={"description": "use TLS for the connection"})
    
    def execute(self):
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = self.subject if self.subject else "Do Not Reply - Mail from " + self.cname()
        message["From"] = self.mail_account
        message["To"] = ", ".join(self.recipients)
        
        mt = MIMEText(self.body, "html")
        
        message.attach(mt)
        
        # Send
        try:
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                if self.tls:
                    server.starttls()  # Secure the connection
                if self.pw is not None:
                    server.login(self.mail_account, self.pw)
                server.sendmail(self.mail_account, self.recipients, message.as_string())
                #print("✅ Email sent successfully.")
        except Exception as e:
            raise StatemachineException("could not send mail from " + self.cname()) from e