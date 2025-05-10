from abc import ABC, abstractmethod

from PyDataGrabber.src.grabber.GrabberElement import GrabberElement

class Buffer(GrabberElement, ABC):
    """
    Abstract base class for buffers.
    """
    
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity
    
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