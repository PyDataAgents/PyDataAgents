from abc import abstractmethod
from typing import TYPE_CHECKING

from pydag.agents.AgentStates import AdapterState

from .Adapter import Adapter

if TYPE_CHECKING:
    from ..buffers.Buffer import Buffer

class SubscribeAdapter(Adapter):
    """abstract class for `Adapter` Interface for subscribing from data sources
       <br>new `Adapters` that allow for subscribing to a source via callback must inherit this class next to `Adapter`.
    """
    
    @abstractmethod
    def _on_subscribe(self, buffers : dict[str, 'Buffer'], addresses : list[str], sampling_period : int, n : int):
        """subscribe logic from source into specified buffers and addresses, with specified sampling_period and n samples at once
        """        
    
    def subscribe(self, buffers : dict[str, 'Buffer'], addresses : list[str], sampling_period : int, n : int):
        """subscribes to data from source into specified buffers and addresses, with specified sampling_period and n samples at once
        """
        self._state = AdapterState.SUBSCRIBING
        self._on_subscribe(buffers, addresses, sampling_period, n)
    
    @abstractmethod
    def _on_unsubscribe(self):
        """ unsubscribe logic to stop subscribing
        """
    
    def unsubscribe(self):
        """resets the subscription
        """
        self._on_unsubscribe()
        self._state = AdapterState.CONNECTED  