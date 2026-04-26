from abc import abstractmethod
from typing import TYPE_CHECKING


from ..agents.AgentStates import AdapterState
from .Adapter import Adapter

if TYPE_CHECKING:
    from ..buffers.Buffer import Buffer

class PublishAdapter(Adapter):
    """abstract class for `Adapter` Interface for publishing to data sinks.
       <br>new `Adapters` that allow for publishing to a sink via callback must inherit this class next to `Adapter`.
    """
    
    @abstractmethod
    def _on_publish(self, buffers : dict[str, 'Buffer'], addresses : list[str], sampling_period : int, n : int, persistent : bool, error_callback : callable = None):
        """publish logic for samples from buffers to addresses with specified sampling_period and n samples at once
            <br>if persistent is specified False, then the samples will be removed from buffers.
            The method must non-blocking.

        Args:
            buffers (dict[str, Buffer]): _description_
            addresses (list[str]): _description_
            sampling_period (int): _description_
            n (int): _description_
            persistent (bool): _description_
            error_callback (callable, optional): Callback that can be used to handle errors in publishing logic. Defaults to None.
            
        Raises:
            AdapterException: if an error occurs during publishing
        """
    
    def publish(self, buffers : dict[str, 'Buffer'], addresses : list[str], sampling_period : int, n : int, persistent : bool):
        """publish samples from buffers to addresses with specified sampling_period and n samples at once
            <br>if persistent is specified False, then the samples will be removed from buffers

        Args:
            buffers (dict[str, Buffer]): _description_
            addresses (list[str]): _description_
            sampling_period (int): _description_
            n (int): _description_
            persistent (bool): _description_
            
        Raises:
            AdapterException: if an error occurs during publishing
        """
        self._check_state(AdapterState.PUBLISHING)
        self._state = AdapterState.PUBLISHING
        self._on_publish(buffers, addresses, sampling_period, n, persistent)
        
    
    @abstractmethod
    def _on_unpublish(self):
        """ unpublish logic to stop publishing
        
        Raises:
            AdapterException: if an error occurs during unpublishing
        """
        
    def unpublish(self):
        """ resets the adapter to stop publishing
        
        Raises:
            AdapterException: if an error occurs during unpublishing
        """
        self._check_state(AdapterState.CONNECTED)
        self._on_unpublish()
        self._state = AdapterState.CONNECTED
    