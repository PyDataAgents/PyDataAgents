from dataclasses import dataclass, field
from PyDataGrabber.statemachine.BufferNode import BufferNode
from PyDataGrabber.statemachine.GrabberNode import GrabberNode

@dataclass
class ConfigureElementAction(GrabberNode, BufferNode):
    
    option : str = field(default=None, metadata={"description": "option to configure with new value"})
    element_id : str = field(default=None, metadata={"description": "id of the element to change the option for"})
        
    def __init__(self):
        super().__init__()
        
    def execute(self):
        