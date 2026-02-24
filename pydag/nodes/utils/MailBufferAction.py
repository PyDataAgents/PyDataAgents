from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from loguru import logger

from ..NodeException import NodeException
from ..Action import Action
from ..BufferNode import BufferNode
from ...utils.DataUtils import DataUtils


@dataclass
class MailBufferAction(BufferNode, Action):
    """An `Action` that send emails based on data from parent `Buffer`.

    This action expects the parent buffer to provide exactly three input keys
    (in this fixed order): `recipients`, `subject`, and `body`.

    Behavior:
        - `recipients` may be a single email address (string) or a comma-separated
            string / list of addresses accepted by the underlying SMTP `sendmail` call.
        - `subject` and `body` are used to populate the message's Subject header
            and HTML body respectively.
        - The action connects to `smtp_server`:`port` and optionally starts TLS
            (when `tls` is True). If `pw` is provided the action will attempt to
            authenticate using `mail_account`/`pw`.
        - When `debug_mode` is True, messages are not sent but logged for
            inspection.

    Raises:
            NodeException: if input keys are missing/invalid or if sending fails.
    """
    smtp_server : str = field(default=None, metadata={"description": "host of the mail server to use"})
    port : int = field(default=None, metadata={"description": "port of the smtp server"})
    mail_account : str = field(default=None, metadata={"description": "mail account to use for login"})
    pw : str = field(default=None, metadata={"description": "password of the mail server"})
    tls : bool = field(default=True, metadata={"description": "use TLS for the connection"})
    debug_mode : bool = field(default=False, metadata={"description": "if set to true, no mails are send, but only logged to console"})
    input_keys : list[str] = field(default_factory=lambda: ["recipients", "subject", "body"], metadata={"description": "the input keys must be 3 in total and in the fixed order: recipients, subject and body"})
    persistent : bool = field(default=False, metadata={"description": "by default, sent mails are removed from buffer"})
    n : int = field(default=0, metadata={"description": "all buffer samples are extracted at once"})
    
    def _on_execute(self):
        # get data
        data = self.get_parent_data()
        if len(data) > 0:
            if len(data.keys()) != 3:
                logger.debug("incorrect number of input keys (must be 3) for " + self.__class__.__name__)
                return
                #raise NodeException("incorrect number of input keys (must be 3) for " + self.cname())
            # create row data
            rows = DataUtils.dict_to_list(data)
            for row in rows:
                recipients = row[self.input_keys[0]]
                if isinstance(recipients, str):
                    recipients = [recipients]
                subject = row[self.input_keys[1]]
                body = row[self.input_keys[2]]
                if recipients is None or subject is None or body is None:
                    logger.warning(f"Skipping a mail to {recipients} due to missing data.")
                    continue
                # Create message
                message = MIMEMultipart("alternative")
                message["Subject"] = Header(subject, 'utf-8').encode()
                message["From"] = self.mail_account
                message["To"] = ", ".join(recipients)
                
                mt = MIMEText(body, "html")
                
                message.attach(mt)
                
                # Send mail
                logger.debug(f'\n-----------------------------\n{self.mail_account} -> {recipients}\n{subject}\n\n{message.as_string()}\n--------------------------\n')
                if self.debug_mode:
                    return
                else:        
                    try:
                        with smtplib.SMTP(self.smtp_server, self.port) as server:
                            if self.tls:
                                server.starttls()  # Secure the connection
                            if self.pw is not None:
                                server.login(self.mail_account, self.pw)                
                            server.sendmail(self.mail_account, recipients, message.as_string())
                    except Exception as e:
                        raise NodeException("could not send mail from " + self.__class__.__name__) from e