from abc import ABC, abstractmethod

from PyDataGrabber.src.grabber.GrabberElement import GrabberElement

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
    def install(self):
        """
        install the adapter / initialize object.
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
    
    