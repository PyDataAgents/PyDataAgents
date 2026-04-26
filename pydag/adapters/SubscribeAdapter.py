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
    def _on_subscribe(self, buffers : dict[str, 'Buffer'], addresses : list[str], sampling_period : int, n : int, error_callback : callable = None):
        """subscribe logic from source into specified buffers and addresses, with specified sampling_period and n samples at once
        
        Args:
            buffers (dict[str, Buffer]): buffer objects to subscribe data into
            addresses (list[str]): address identifiers to subscribe to, the interpretation of the addresses depends on the implementation of the adapter
            sampling_period (int): sampling period in ms between samples, if 0 then process samples as fast as possible
            n (int): number of samples to process each iteration, if 0 then process all available samples at once
            error_callback (callable, optional): Callback that can be used to handle errors in subscribing logic. Defaults to None.
        
        """        
    
    def subscribe(self, buffers : dict[str, 'Buffer'], addresses : list[str], sampling_period : int, n : int, error_callback : callable = None):
        """subscribes to data from source into specified buffers and addresses, with specified sampling_period and n samples at once
        """
        self._check_state(AdapterState.SUBSCRIBING)
        self._state = AdapterState.SUBSCRIBING
        self._on_subscribe(buffers, addresses, sampling_period, n, error_callback)
    
    @abstractmethod
    def _on_unsubscribe(self):
        """ unsubscribe logic to stop subscribing
        """
    
    def unsubscribe(self):
        """resets the subscription
        """
        self._check_state(AdapterState.CONNECTED)
        self._on_unsubscribe()
        self._state = AdapterState.CONNECTED  