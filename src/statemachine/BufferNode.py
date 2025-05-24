from dataclasses import dataclass, field
from PyDataGrabber.src.buffers.Buffer import Buffer
from PyDataGrabber.src.statemachine.Node import Node

@dataclass
class BufferNode(Node):
    
    buffer_id : str = field(default=None, metadata={"description": "ID of the buffer"})
    
    def __init__(self):
        super().__init__()
        self.buffer : Buffer = None  # Placeholder for the buffer instance