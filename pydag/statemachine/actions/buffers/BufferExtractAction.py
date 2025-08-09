from dataclasses import dataclass, field

from ....buffers.DictBuffer import DictBuffer
from ...StatemachineException import StatemachineException
from ...Action import Action
from ...BufferNode import BufferNode


@dataclass
class BufferExtractAction(BufferNode, Action):
    """
    `Action` for extracting data from the parents' buffers to store into this buffer.
    This `Action` can only be applied on if the parents' buffers is of type `DictBuffer`.
    """
    
    extract_keys : list[str] = field(default_factory=list, metadata={"description": "keys to search for in the parent buffers and extract their values into this element's buffer"})
            
    def execute(self):
        for parent in self.parents:
            if not isinstance(parent, BufferNode):
                raise StatemachineException("parents must be of type " + BufferNode.cname())
            else:
                if not isinstance(parent.buffer, DictBuffer):
                    raise StatemachineException("parents' buffers must be of type " + DictBuffer.cname())
            d = {}
            for key in self.extract_keys:
                bd = parent.buffer.data()
                if key in bd:
                    d[key] = bd[key]
            self.buffer.push(d)
            
                  
                        
                    
    