from __future__ import annotations
from abc import abstractmethod
from ..agents.AgentElement import AgentElement

class Adapter(AgentElement):
    """
    Abstract base class for `Adapters`. All `Adapters` must inherit from this class.
    """
    
    ADDRESS = "address"
    ADDRESSES = "addresses"
    __post_init__
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
    
    