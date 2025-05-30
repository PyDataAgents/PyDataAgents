from dataclasses import dataclass, field
from PyDataGrabber.buffers.Buffer import Buffer
from PyDataGrabber.grabbers.Grabber import Grabber
from PyDataGrabber.statemachine.Node import Node
from PyDataGrabber.statemachine.StatemachineException import StatemachineException

@dataclass
class BufferNode(Node):
    
    buffer_id : str = field(default=None, metadata={"description": "unique ID of the buffer"})
    
    def __init__(self):
        super().__init__()
        self.buffer : Buffer = None  # Placeholder for the buffer instance
        
    def install(self, grabber : Grabber = None):
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
                raise StatemachineException("No " + Buffer.cname() + " with id=" + self.buffer_id + " exists in " + Grabber.cname())
        
    def deinstall(self, grabber : Grabber = None):
        super().deinstall(grabber)
        self.buffer : Buffer = None
            