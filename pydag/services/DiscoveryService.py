from abc import abstractmethod
from dataclasses import dataclass


from .ObserverService import ObserverService


@dataclass
class DiscoveryService(ObserverService):
    """ `Service` Interface for discovering available data sources and their addresses.
       <br>new `Service` that allow for discovery of sources and addresses must inherit this class next to `Service`.

    Args:
        ObserverService (_type_): parent class for all Service, provides basic connection management and state handling
    """
    
    @abstractmethod
    def discover(self) -> list[dict]:
        """ discovery logic to find available data sources and their config options
        
        Raises:
            ServiceException: if an error occurs during discovery
        """