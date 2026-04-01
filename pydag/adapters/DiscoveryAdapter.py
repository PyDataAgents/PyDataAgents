from abc import abstractmethod


from pydag.agents.AgentStates import AdapterState
from .Adapter import Adapter


class DiscoveryAdapter(Adapter):
    """ `Adapter` Interface for discovering available data sources and their addresses.
       <br>new `Adapters` that allow for discovery of sources and addresses must inherit this class next to `Adapter`.

    Args:
        Adapter (_type_): parent class for all Adapters, provides basic connection management and state handling
    """
    
    @abstractmethod
    def _on_discover(self):
        """ discovery logic to find available data sources and their config options
        
        Raises:
            AdapterException: if an error occurs during discovery
        """
        
    def discover(self) -> list[dict]:
        """ discovers available data sources and their config options
        
        Raises:
            AdapterException: if an error occurs during discovery
        """
        self._check_state(AdapterState.DISCOVERING)
        self._state = AdapterState.DISCOVERING
        discovered_config : list[dict] = self._on_discover()
        self._state = AdapterState.CONNECTED
        return discovered_config