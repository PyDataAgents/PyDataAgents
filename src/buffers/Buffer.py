import json
from abc import abstractmethod
from PyDataGrabber.src.buffers.DataType import DataType
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement


class Buffer(GrabberElement):
    """
    Abstract base class for buffers.
    """
    
    def __init__(self, id : str = None, capacity : int = 1, data_type : list[DataType] = None, unit : list[str] = None, initial_values : any = None, description : str = None):
        super().__init__(id)
        self.capacity = capacity
        self.initial_values = initial_values
        self.description = description
        self.data_type = data_type
        self.unit = unit
    
    @abstractmethod
    def push(self, elements):
        """
        push new elements to buffer
        """
        pass
        
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
        pass
    
    def data_with_meta(self, n : int = 0, persistent : bool = True) -> dict:
        d = {}
        d["data"] = self.data(n, persistent)
        d["meta"] = self.config_options()
        return d
    
    def json(self, n=None, persistent=True):
        return json.dumps(self.data_with_meta(n, persistent))

    def __str__(self):
        """string representation

        Returns:
            str: string represenation as json
        """
        return self.json(n = 0, persistent=True)

    def config_options(self) -> dict:
        d = super().config_options()
        d["capacity"] = self.capacity
        if self.data_type is not None:
            d["data_type"] = self.data_type
        if self.unit is not None:
            d["unit"] = self.unit
        if self.initial_values is not None:
            d["initial_values"] = self.initial_values
        if self.description is not None:
            d["description"] = self.description
        return d
    
        
        