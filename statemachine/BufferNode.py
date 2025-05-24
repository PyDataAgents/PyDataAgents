from dataclasses import dataclass, field
from PyDataGrabber.buffers.Buffer import Buffer
from PyDataGrabber.statemachine.Node import Node

@dataclass
class BufferNode(Node):
    
    buffer_id : str = field(default=None, metadata={"description": "ID of the buffer"})
    
    def __init__(self):
        super().__init__()
        self.buffer : Buffer = None  # Placeholder for the buffer instance