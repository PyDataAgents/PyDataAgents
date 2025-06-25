from dataclasses import dataclass, field

from ...statemachine.actions.MailAction import MailAction


@dataclass
class FolderObserveMailService:
    """
    `Service` to observe a folder for new files and alert by mail on events.
    """
    
    mail_action : MailAction = field(default_factory=None, )

    def __init__(self):
        super().__init__()        

    def start(self):
        pass
        

    def stop(self):
        pass

    