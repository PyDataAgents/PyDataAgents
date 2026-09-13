from dataclasses import dataclass, field


from..NodeException import NodeException
from ...services.office.MSGraphService import MSGraphService
from ..ServiceNode import ServiceNode
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class OutlookMailAction(BufferNode, ServiceNode, Action):
    
    user : str = field(default=None, metadata={"description": "user mail or id of the account that shall send the mail"})
    recipients : str | list[str] = field(default_factory=list[str], metadata={"description": "mail address of the recipient"})
    subject : str = field(default=None,  metadata={"description": "subject of the mail"})
    body : str = field(default=None,  metadata={"description": "body of the mail"})        
    
    def _on_install(self, agent = None):
        super()._on_install(agent)
        BufferNode._on_install(self, agent)
        ServiceNode._on_install(self, agent)
        if not isinstance(self._service, MSGraphService):
            raise NodeException("referenced service is not an instance of " + MSGraphService.cname())
        
    def _on_execute(self):
        if isinstance(self._service, MSGraphService):
            recipients = self.recipients if isinstance(self.recipients, list) else [self.recipients]
            if self.user:
                self._service.sendmail(self.user, self.subject, self.body, recipients)
            else:
                self._service.me_sendmail(self.subject, self.body, recipients)