from dataclasses import dataclass, field
from ..buffers.Buffer import Buffer
from ..agents.Agent import Agent
from .Node import Node
from .StatemachineException import StatemachineException

@dataclass
class BufferNode(Node):
    
    buffer_id : str = field(init=True, default=None, metadata={"description": "unique ID of the buffer"})
    
    def __init__(self):
        super().__init__()
        self.buffer : Buffer = None  # Placeholder for the buffer instance
        
    def install(self, grabber : Agent = None):
        """this `install` method connects a `Buffer` instance from specified `grabber` based on given `buffer_id`

        Args:
            grabber (Grabber, optional): grabber instance. Defaults to None.

        Raises:
            StatemachineException: throws an `Exception` if no `buffer` with the specified `buffer_id` can be found in `grabber`
        """
        super().install(grabber)
        if self.buffer is None:
            if self.buffer_id in grabber.buffer_store:
                self.buffer = grabber.buffer_store[self.buffer_id]
            else:
                raise StatemachineException("No " + Buffer.cname() + " with id=" + self.buffer_id + " exists in " + Agent.cname())
        
    def deinstall(self, grabber : Agent = None):
        super().deinstall(grabber)
        self.buffer : Buffer = None
            