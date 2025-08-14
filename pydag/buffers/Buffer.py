from __future__ import annotations
from dataclasses import dataclass, field
import json
from abc import abstractmethod
from .DataType import DataType
from ..agents.AgentElement import AgentElement

@dataclass
class Buffer(AgentElement):
    """
    Abstract base class for buffers.
    """    
    
    capacity : int = field(default=1, metadata={"description": "Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer."})
    data_type : str = field(default=DataType.FLOAT.value, metadata={"description": "datatype to expect from buffer elements, can be DataType enum or list of enums"})
    initial_values : any = field(default=None, metadata={"description": "initial values in buffer"})
    unit : any = field(default=None, metadata={"description": "unit of element values in this buffer, can be string or list of strings"})
    description : str = field(default=None, metadata={"description": "buffer description"})

    def __post_init__(self):
        super().__post_init__()
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

    @abstractmethod
    def size(self) -> int:
        """returns the size of the buffer

        Returns:
            int: number of samples
        """

    @abstractmethod
    def data_with_meta(self, n : int = 0, persistent : bool = True) -> dict:
        pass

    def json(self, n=None, persistent=True):
        return json.dumps(self.data_with_meta(n, persistent), ensure_ascii=False)

    def __str__(self):
        """string representation

        Returns:
            str: string represenation as json
        """
        return self.json(n = 0, persistent=True)    
        
        