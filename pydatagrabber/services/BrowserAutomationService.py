from dataclasses import dataclass, field
from selenium import webdriver
from .Service import Service

@dataclass
class BrowserAutomationService(Service):
    
    browser_type : str = field(default="EDGE", metadata={"description": "type of browser, EDGE | FIREFOX | CHROME"})
    
    def __init__(self):
        super().__init__()
        self.driver : webdriver.Edge = None
        
    def start(self):
        match self.browser_type:
            case "EDGE":
                self.driver = webdriver.Edge()
            case "FIREFOX":
                self.driver = webdriver.Firefox()
            case "CHROME":
                self.driver = webdriver.Chrome()
    
    def stop(self):
        self.driver.quit()
    