from dataclasses import dataclass, field

from ...services.Service import Service
from ...nodes.NodeException import NodeException
from ...agents.Agent import Agent
from ...services.browser.BrowserAutomationService import BrowserAutomationService
from ..Action import Action
from ..ServiceNode import ServiceNode


@dataclass
class BrowserAutomationAction(ServiceNode, Action):
    
    service_id : str = field(default=None, metadata={"description" : "ID of the service to reference for Browser Automation"})
    
    def __post_init__(self):
        super().__post_init__()
        self.service : BrowserAutomationService = None
    
    def install(self, agent : Agent = None):
        if self.service is None:
            if self.service_id in agent.service_store:
                if isinstance(agent.service_store[self.service_id], BrowserAutomationService):
                    self.service = agent.service_store[self.service_id]
                else:
                    raise NodeException("the specified " + Service.cname() + " is not of instance " +  BrowserAutomationService.cname())
            else:
                raise NodeException("The specified service_id=" + self.service_id + " could not be found in " + agent.cname())