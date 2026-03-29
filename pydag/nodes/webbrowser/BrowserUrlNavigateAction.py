from dataclasses import dataclass, field
import time

from ...services.Service import Service
from ...nodes.NodeException import NodeException
from ...services.webbrowser.BrowserAutomationService import BrowserAutomationService
from .BrowserAutomationAction import BrowserAutomationAction

@dataclass
class BrowserUrlNavigateAction(BrowserAutomationAction):
    """`Action` for navigating a Browser Automation Object to a new url

    Raises:
        NodeException: if referenced `self._service`  is not of type `BrowserAutomationService`
    """
    
    url : str = field(default=None, metadata={"description" : "url to navigate to in browser"})
    sleep_time : float = field(default=0.0, metadata={"description" : "time to wait after navigation (in seconds)"})
               
    def _on_execute(self):
        if isinstance(self._service, BrowserAutomationService):
            self._service.get_driver().get(self.url)
            time.sleep(self.sleep_time)
        else:
            raise NodeException(Service.cname() + " is not of type " + BrowserAutomationService.cname())