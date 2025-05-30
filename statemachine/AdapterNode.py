from dataclasses import dataclass, field
from PyDataGrabber.adapters.Adapter import Adapter
from PyDataGrabber.grabbers.Grabber import Grabber
from PyDataGrabber.statemachine.BufferNode import BufferNode
from PyDataGrabber.statemachine.StatemachineException import StatemachineException

@dataclass
class AdapterNode(BufferNode):
    """
    AdapterNode is a specialized BufferNode that integrates an adapter for data processing.
    It inherits from BufferNode to manage buffers and provides methods to interact with the adapter.
    """
    
    adapter_id: str = field(default=None, metadata={"description": "ID of the adapter"})

    def __init__(self):
        super().__init__()
        self.adapter : Adapter = None
        
    def install(self, grabber : Grabber = None):
        super().install(grabber)
        if self.adapter is None:
            if self.adapter_id in grabber.adapter_store:
                self.adapter = grabber.adapter_store[self.adapter_id]
            else:
                raise StatemachineException("No " + Adapter.cname() + " with id=" + self.adapter_id + " was found in " + grabber.cname())
    
    def deinstall(self, grabber : Grabber = None):
        super().deinstall(grabber)
        self.adapter = None
