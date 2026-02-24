from abc import abstractmethod
from typing import TYPE_CHECKING

from pydag.agents.AgentStates import AdapterState

from .Adapter import Adapter

if TYPE_CHECKING:
    from ..buffers.Buffer import Buffer
    
    
class ReadAdapter(Adapter):
    """abstract class for `Adapter` Interface for reading from data sources.
       <br>new `Adapters` that allow for reading from a source via one-shot polling must inherit this class next to `Adapter`.
    """
    
    @abstractmethod
    def _on_read(self, buffers : dict[str, 'Buffer'], addresses : list[str], n : int = 0):
        """ read logic from source into buffers for specified addresses and n samples at once

        Args:
            buffers (dict[str, Buffer]): _description_
        """
    
    def read_from_source(self, buffers : dict[str, 'Buffer'], addresses : list[str], n : int = 0):
        """ reads data from source into buffers for specified addresses and n samples at once

        Args:
            buffers (dict[str, Buffer]): _description_
            addresses (list[str]): _description_
            n (int): _description_
        """
        self._state = AdapterState.READING
        self._on_read(buffers, addresses, n)
        self._state = AdapterState.CONNECTED