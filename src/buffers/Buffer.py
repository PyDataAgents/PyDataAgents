from dataclasses import dataclass, field
import json
from abc import abstractmethod
from PyDataGrabber.src.buffers.DataType import DataType
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement

@dataclass
class Buffer(GrabberElement):
    """
    Abstract base class for buffers.
    """
    
    capacity : int = field(default=1, metadata={"description": "number of elements that can be stored in buffer before being discarded in FiFo fashion"})
    data_type : str = field(default=DataType.NUMERIC.value, metadata={"description": "datatype to expect from buffer elements, can be DataType enum or list of enums"})
    initial_values : any = field(default=None, metadata={"description": "initial values in buffer"})
    unit : any = field(default=1, metadata={"description": "unit of element values in this buffer, can be string or list of strings"})
    description : str = field(default=1, metadata={"description": "buffer description"})
    
    
    def __init__(self):
        super().__init__()        
        self.elements = any
    
    @abstractmethod
    def push(self, elements):
        """
        push new elements to buffer
        """
        
    @abstractmethod
    def data(self, n=0, persistent=True) -> any:
        """
        get the buffers data, or n samples, with persistent True/False you specify whether to keep the elements in buffer
        the return type depends on the buffer implementation
        """
        pass
    
    @abstractmethod
    def size(self) -> int:
        """returns the size of the buffer

        Returns:
            int: number of samples
        """
    
    def data_with_meta(self, n : int = 0, persistent : bool = True) -> dict:
        d = {}
        d["data"] = self.data(n, persistent)
        d["meta"] = self.config_options()
        return d
    
    def json(self, n=None, persistent=True):
        return json.dumps(self.data_with_meta(n, persistent), ensure_ascii=False)

    def __str__(self):
        """string representation

        Returns:
            str: string represenation as json
        """
        return self.json(n = 0, persistent=True)    
        
        