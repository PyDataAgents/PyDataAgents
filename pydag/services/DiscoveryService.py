from abc import abstractmethod
from dataclasses import dataclass


from .ObserverService import ObserverService


@dataclass
class DiscoveryService(ObserverService):
    """ `Adapter` Interface for discovering available data sources and their addresses.
       <br>new `Adapters` that allow for discovery of sources and addresses must inherit this class next to `Adapter`.

    Args:
        Adapter (_type_): parent class for all Adapters, provides basic connection management and state handling
    """
    
    @abstractmethod
    def _discover(self) -> list[dict]:
        """ discovery logic to find available data sources and their config options
        
        Raises:
            AdapterException: if an error occurs during discovery
        """