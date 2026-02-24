from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from loguru import logger

from ..NodeException import NodeException
from ..Action import Action


@dataclass
class MailAction(Action):
    
    smtp_server : str = field(default=None, metadata={"description": "host of the mail server to use"})
    port : int = field(default=None, metadata={"description": "port of the smtp server"})
    mail_account : str = field(default=None, metadata={"description": "mail account to use for login"})
    pw : str = field(default=None, metadata={"description": "password of the mail server"})
    recipients : str | list[str] = field(default_factory=list[str], metadata={"description": "mail address of the recipient"})
    subject : str = field(default=None,  metadata={"description": "subject of the mail"})
    body : str = field(default=None,  metadata={"description": "body of the mail"})
    tls : bool = field(default=True, metadata={"description": "use TLS for the connection"})
    debug_mode : bool = field(default=False, metadata={"description": "if set to true, no mails are send, but only logged to console"})
    
    def _on_execute(self):
        if isinstance(self.recipients, str):
            self.recipients = [self.recipients]
        
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
                if self.debug_mode:
                    logger.debug(f'{self.mail_account} -> {self.recipients}:\n{message.as_string()}')
                else:
                    if self.tls:
                        server.starttls()  # Secure the connection
                    if self.pw is not None:
                        server.login(self.mail_account, self.pw)                
                    server.sendmail(self.mail_account, self.recipients, message.as_string())
        except Exception as e:
            raise NodeException("could not send mail from " + self.cname()) from e