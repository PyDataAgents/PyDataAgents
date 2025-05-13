from abc import ABC, abstractmethod

from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement

class Adapter(GrabberElement, ABC):
    """
    Abstract base class for data adapters.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        connect to the data source.
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        disconnect from the data source.
        """
        pass
    
    