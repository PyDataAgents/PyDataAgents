from dataclasses import dataclass, field

from ....buffers.DictBuffer import DictBuffer
from ....grabbers.Grabber import Grabber
from ...Action import Action
from ...BufferNode import BufferNode


@dataclass
class DataElementAction(BufferNode, Action):
    
    n : int = field(default=0, metadata={"description": "Number of samples to retrieve from the parents' buffers."})
    persistent : bool = field(default=False, metadata={"description": "if true, data will persist in parents' buffers after retrieval"})
    
    MAX_DEFAULT_CAPACITY = 1e6
        
    def __init__(self):
        super().__init__()
           
    def install(self, grabber : Grabber = None):
        if self.buffer is None:
            if grabber is not None:
                if self.buffer_id in grabber.buffer_store:
                    self.buffer = grabber.buffer_store[self.buffer_id]
            else:
                self.buffer = DictBuffer()
                self.buffer.id = self.id + "-BUFFER"
                self.buffer.capacity = DataElementAction.MAX_DEFAULT_CAPACITY
                if grabber is not None:
                    grabber.add_buffer(self.buffer)
        super().install(grabber)
    