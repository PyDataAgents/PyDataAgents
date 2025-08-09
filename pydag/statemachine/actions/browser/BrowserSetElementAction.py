from dataclasses import dataclass, field

from ...BufferNode import BufferNode
from .BrowserAutomationAction import BrowserAutomationAction

@dataclass
class BrowserSetElementAction(BrowserAutomationAction, BufferNode):
    
    xpath : str = field(default=None, metadata={"description": "XPath definition to locate the element to set a value to"})
               
    def execute(self):
        pass 