from abc import ABC, abstractmethod

from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement

class Buffer(GrabberElement, ABC):
    """
    Abstract base class for buffers.
    """
    
    def __init__(self, id: str = None, capacity: int = 1, initial_values: any = None, description: str = None):
        super().__init__()
        self.id = id
        self.capacity = capacity
        self.initial_values = initial_values
        self.description = description
    
    @abstractmethod
    def push(self, objects):
        """
        push new objetcs to buffer
        """
        pass
    
    @abstractmethod
    def data(self, n=None, persistent=True) -> dict:
        """
        get the buffers data, or n samples, with persistent True/False you specify whether to keep the elements in buffer
        """
        pass

    @abstractmethod
    def size(self) -> int:
        """returns the size of the buffer

        Returns:
            int: number of samples
        """
        pass

    @abstractmethod
    def json(self, n=None, persistent=True):
        """_summary_

        Args:
            n (_type_, optional): _description_. Defaults to None.
            persistent (bool, optional): _description_. Defaults to True.
        """
        pass

    def config_options(self) -> dict:
        d = super().config_options()
        d["capacity"] = self.capacity
        if self.initial_values != None:
            d["initial_values"] = self.initial_values
        if self.description != None:
            d["description"] = self.description
        return d
        