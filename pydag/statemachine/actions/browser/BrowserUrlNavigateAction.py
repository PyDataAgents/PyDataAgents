from dataclasses import dataclass, field

from .BrowserAutomationAction import BrowserAutomationAction

@dataclass
class BrowserUrlNavigateAction(BrowserAutomationAction):
    
    url : str = field(default=None, metadata={"description" : "url to navigate to in browser"})
               
    def execute(self):
        self.service.driver.get(self.url)