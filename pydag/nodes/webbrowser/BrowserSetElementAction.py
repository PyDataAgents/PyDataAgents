from dataclasses import dataclass, field
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


from ...agents.Agent import Agent
from ...nodes.NodeException import NodeException
from ...services.webbrowser.BrowserAutomationService import BrowserAutomationService
from ...nodes.BufferNode import BufferNode
from .BrowserAutomationAction import BrowserAutomationAction

@dataclass
class BrowserSetElementAction(BrowserAutomationAction, BufferNode):
    
    xpath : str = field(default=None, metadata={"description": "XPath definition to locate the element to set a value to"})
    persistent : bool = field(default=False, metadata={"description": "specifies whether data is removed (False) from parent or not (True)"})
    n : int = field(default=1, metadata={"description": "specifies how much data is retrieved from parent buffer. Here Default 1 -> only one value per Set Action"})
    
    def _on_install(self, agent : Agent = None):
        BrowserAutomationAction._on_install(self, agent)
        BufferNode._on_install(self, agent)
                   
    def _on_execute(self):
        if isinstance(self._service, BrowserAutomationService):
            try:
                element : WebElement = self._service.get_driver().find_element(By.XPATH, self.xpath)
                data = self.get_parent_data()
                if len(data.keys()) > 1:
                    raise NodeException("only one data column should be provided for this Node (use input_keys or ignore_keys to reduce the data)")
                value = next(iter(data.values()))[0]
                element.send_keys(value)
                self.add_data(value)
            except NoSuchElementException as nsee:
                raise NodeException(f"could not find element by xpath={self.xpath}") from nsee            
        else:
            raise NodeException(f"{self._service.cname()} is not of type {BrowserAutomationService.cname()}")