from abc import abstractmethod

from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement

class Adapter(GrabberElement):
    """
    Abstract base class for data adapters.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """
        connect to the data source/sink.
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        disconnect from the data source/sink.
        """
        pass
    
    