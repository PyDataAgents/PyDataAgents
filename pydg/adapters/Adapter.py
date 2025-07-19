from __future__ import annotations
from abc import abstractmethod
from ..grabbers.GrabberElement import GrabberElement

class Adapter(GrabberElement):
    """
    Abstract base class for `Adapters`. All `Adapters` must inherit from this class.
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
    
    