from dataclasses import dataclass, field

from ...services.Service import Service
from ...grabbers.Grabber import Grabber
from ...statemachine.StatemachineException import StatemachineException
from ...services.BrowserAutomationService import BrowserAutomationService
from ..Action import Action
from ..ServiceNode import ServiceNode

@dataclass
class UrlNavigateAction(ServiceNode, Action):
    
    service_id : str = field(default=None, metadata={"description" : "ID of the service to reference for Browser Automation"})
    url : str = field(default=None, metadata={"description" : "url to navigate to in browser"})
    
    def __init__(self):
        self.service : BrowserAutomationService = None
    
    def install(self, grabber : Grabber = None):
        if self.service is None:
            if self.service_id in grabber.service_store:
                if isinstance(grabber.service_store[self.service_id], BrowserAutomationService):
                    self.service = grabber.service_store[self.service_id]
                else:
                    raise StatemachineException("the specified " + Service.cname() + " is not of instance " +  BrowserAutomationService.cname())
            else:
                raise StatemachineException("The specified service_id=" + self.service_id + " could not be found in " + Grabber.cname())
    
    def deinstall(self, grabber = None):
        self.service = None
        
    def execute(self):
        self.service.driver.get(self.url)