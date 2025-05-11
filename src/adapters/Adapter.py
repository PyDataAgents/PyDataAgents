from abc import ABC, abstractmethod

from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement

class Adapter(GrabberElement, ABC):
    """
    Abstract base class for data adapters.
    """
    
    @abstractmethod
    def validate(self):
        """
        validate the adapter configuration.
        """
        pass
    
    @abstractmethod
    def connect(self):
        """
        connect to the data source.
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """
        disconnect from the data source.
        """
        pass
    
    @abstractmethod
    def isConnected(self):
        """
        check if the adapter is connected to the data source.
        """
        pass
    
    