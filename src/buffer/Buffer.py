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
    
    def data(self, n=None, persistent=True):
        """
        get the buffers data, or n samples, with persistent True/False you specify whether to keep the elements in buffer
        """
        pass