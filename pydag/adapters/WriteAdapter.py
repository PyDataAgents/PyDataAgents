from abc import abstractmethod
from typing import TYPE_CHECKING

from pydag.agents.AgentStates import AdapterState

from .Adapter import Adapter

if TYPE_CHECKING:
    from ..buffers.Buffer import Buffer

class WriteAdapter(Adapter):
    """abstract class for Adapter Interface for writing to data sinks
       <br>new `Adapters` that allow for writing to a sink via one-shot polling must inherit this class next to `Adapter`.
    """
    
    @abstractmethod
    def _on_write(self, buffers : dict[str, 'Buffer'], addresses : list[str], n : int, persistent : bool):
        """ write logic from buffers to sink, based on specified addresses and n number of samples
        """
    
    def write_to_sink(self, buffers : dict[str, 'Buffer'], addresses : list[str], n : int, persistent : bool):
        """writes data from buffers to sink, based on specified addresses and n number of samples
        <br>if persistent = False, then the values are removed from buffer on writing

        Args:
            buffers (dict[str, Buffer]): _description_
            addresses (list[str]): _description_
            n (int): _description_
            persistent (bool): _description_
        """
        self._state = AdapterState.WRITING
        self._on_write(buffers, addresses, n, persistent)
        self._state = AdapterState.CONNECTED