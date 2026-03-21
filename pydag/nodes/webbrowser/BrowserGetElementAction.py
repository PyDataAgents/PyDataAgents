from dataclasses import dataclass, field
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


from ...agents.Agent import Agent
from ...nodes.NodeException import NodeException
from ...services.browser.BrowserAutomationService import BrowserAutomationService
from ...nodes.BufferNode import BufferNode
from .BrowserAutomationAction import BrowserAutomationAction

@dataclass
class BrowserGetElementAction(BrowserAutomationAction, BufferNode):
    
    xpath : str = field(default=None, metadata={"description": "XPath definition to locate the element to get a value from"})
    attribute : str = field(default=None, metadata={"description": "specifies the name of the attribute to retrieve data from, defaults to None, then only the inner text of element is retrieved"})
    output_keys : list[str] = field(default_factory=lambda: ["tags", "values"])
    
    def _on_install(self, agent : Agent = None):
        BrowserAutomationAction._on_install(self, agent)
        BufferNode._on_install(self, agent)
               
    def _on_execute(self):
        if isinstance(self._service, BrowserAutomationService):
            elements : list[WebElement] = self._service.get_driver().find_elements(By.XPATH, self.xpath)
            if len(elements) > 0:
                for element in elements:
                    tag = element.tag_name
                    if self.attribute:
                        value = element.get_attribute(self.attribute)
                    else:
                        value = element.text
                    if len(self.output_keys) == 2:
                        dic = dict(zip(self.output_keys, [tag, value]))
                    elif len(self.output_keys) == 1:
                        dic = dict(zip(self.output_keys, [value]))
                    else:
                        raise NodeException(f"output_keys should either be of lenght 1 or 2 (not {len(self.output_keys)})")
                    self.add_data(dic)
            else:
                raise NodeException(f"Could not find element by xpath={self.xpath}")
        else:
            raise NodeException(f"{self._service.cname()} is not of type {BrowserAutomationService.cname()}")
             