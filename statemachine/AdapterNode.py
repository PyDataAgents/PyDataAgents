from dataclasses import dataclass, field
from PyDataGrabber.adapters.Adapter import Adapter
from PyDataGrabber.statemachine.BufferNode import BufferNode

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
