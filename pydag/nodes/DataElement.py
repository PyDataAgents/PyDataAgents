from dataclasses import dataclass, field
from typing import Dict, Tuple

from ..nodes.BufferNode import BufferNode
from ..nodes.Action import Action
from ..agents.AgentConfig import AgentConfig
from .DataElementException import DataElementException
    

@dataclass
class DataElement(BufferNode, Action):
    """Base class for all DataElements.
    This class provides the basic structure and functionality for DataElements.
    """
    
    n : int = field(default=0, metadata={"description": "Number of samples to retrieve from the parents' buffers."})
    persistent : bool = field(default=True, metadata={"description": "if true, data will persist in parents' buffers after retrieval"})
            
    def get_data_size(self) -> int:
        """
        Returns the size of the data in the DataElement's buffer.
        
        Returns:
            int: The size of the data.
        """
        if len(self.parents) > 0:
            if len(self.parents) == 1:
                if isinstance(self.parents[0], BufferNode):
                    return self.parents[0].buffer.size()
                else:
                    raise DataElementException("Parent is not a " + BufferNode.cname())                
            else:
                sizes = []
                for parent in self.parents:
                    if isinstance(parent, BufferNode):
                        sizes.append(parent.buffer.size())
                    else:
                        raise DataElementException("Parent is not a " + BufferNode.cname())
                return max(sizes)
        else:
            return 0
    
    def get_data(self) -> Tuple[Dict, Dict]:
        """
        Method to get the data from the parents' buffer(s).
        """
        if len(self.parents) > 0:
            if len(self.parents) == 1:
                if isinstance(self.parents[0], BufferNode):
                    data = self.parents[0].buffer.data_with_meta(self.n, self.persistent)
                else:
                    raise DataElementException("Parent is not a " + BufferNode.cname())
            else:
                data = {}
                for parent in self.parents:
                    if isinstance(parent, BufferNode):
                        d = parent.buffer.data_with_meta(self.n, self.persistent)
                        for key, value in d.items():
                            if key in data:
                                data[key].extend(value)
                            else:
                                data[key] = [value]
                    else:
                        raise DataElementException("Parent is not a " + BufferNode.cname())
            return data[AgentConfig.DATA], data[AgentConfig.META]
        else:
            return None, None
        
    def set_data(self, data : dict, meta : dict = None):
        """
        Method to set the data for the DataElement's buffer.
        """
        self.buffer.push(data)
        if meta is not None:
            self.__set_meta_data(meta)
    
    def __set_meta_data(self, meta : dict):
        for key in meta:
            if hasattr(self.buffer, key):
                setattr(self.buffer, key, meta[key])