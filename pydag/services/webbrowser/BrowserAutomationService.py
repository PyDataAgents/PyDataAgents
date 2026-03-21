from dataclasses import dataclass, field
from typing import Union
from selenium import webdriver


from ...services.Service import Service


@dataclass
class BrowserAutomationService(Service):
    
    browser_type : str = field(default="EDGE", metadata={"description": "type of browser, EDGE | FIREFOX | CHROME"})
    
    def __post_init__(self):
        super().__post_init__()
        self._driver : Union[webdriver.Edge | webdriver.Firefox | webdriver.Chrome] = None
        
    def _on_start(self):
        match self.browser_type:
            case "EDGE":
                self._driver = webdriver.Edge()
            case "FIREFOX":
                self._driver = webdriver.Firefox()
            case "CHROME":
                self._driver = webdriver.Chrome()
    
    def _on_stop(self):
        self._driver.quit()
        
    def get_driver(self) -> Union[webdriver.Edge | webdriver.Firefox | webdriver.Chrome]:
        return self._driver
    