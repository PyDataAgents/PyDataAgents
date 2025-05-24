from abc import abstractmethod

from PyDataGrabber.grabbers.GrabberElement import GrabberElement

class Adapter(GrabberElement):
    """
    Abstract base class for data adapters.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        connect to the data source/sink.
        """
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        disconnect from the data source/sink.
        """
    
    