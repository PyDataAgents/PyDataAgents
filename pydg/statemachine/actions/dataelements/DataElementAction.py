from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any
from pydg.statemachine.Action import Action
from pydg.statemachine.BufferNode import BufferNode


@dataclass
class DataElementAction(BufferNode, Action):
    
    n : int = field(default=0, metadata={"description": "Number of samples to retrieve from the parents' buffers."})
    persistent : bool = field(default=False, metadata={"description": "if true, data will persist in parents' buffers after retrieval"})
        
    def __init__(self):
        super().__init__()
        
    def execute(self):
        for parent in self.parents:
            if isinstance(parent, BufferNode):
                # Retrieve data from the parent's buffer
                data = parent.buffer.data_with_meta(self.n, self.persistent)
                if data is not None:
                    self.buffer.push(self.transform(data))
        
    @abstractmethod    
    def transform(self, data : dict) -> Any:
        """
        method for transforming data from parents' buffers
        The actual implementation of the transform method should be defined in subclasses.
        """