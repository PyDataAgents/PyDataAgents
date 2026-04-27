from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any


from .ObserverService import ObserverService


@dataclass
class Address():
    """Address class for representing data source addresses in `DiscoveryAdapter`. 
       <br>new address types must inherit this class and implement the required properties and methods.
    """
    source : dict[str, Any] = field(default=None, metadata={"description": "the data source this address belongs to"})
    address : str = field(default=None, metadata={"description": "the actual address string (e.g. topic name, endpoint URL, etc.)"})
    data_type : str = field(default=None, metadata={"description": "the type of data available at this address (e.g. double, int, string, ...)"})
    unit : str = field(default=None, metadata={"description": "the unit of the data available at this address (e.g. \"°C\", \"m/s\", \"USD\", ...)"})
    description : str = field(default=None, metadata={"description": "a human-readable description of the address and the data it provides"})
    
class BrowseFilter():
    """Filter for browsing available addresses in `DiscoveryAdapter`. 
       <br>new filters must inherit this class and implement the `apply` method.
    """
    
    @abstractmethod
    def filter(self, address : Address) -> bool:
        """applies the filter to the given Address and returns True if the address should be included in the browse results, False otherwise

        Args:
            address (Address): The address to filter

        Returns:
            bool: True if the address should be included, False otherwise
        """

@dataclass
class BrowsingService(ObserverService):
    """ `ObserverService` Interface for discovering available data sources and their addresses.
       <br>new `Services` that allow for discovery of sources and addresses must inherit this class.

    """
    
    @abstractmethod    
    def _browse(self, browse_filter : BrowseFilter = None) -> list[Address]:
        """ browses the connected data sources for all available addresses
        
        Raises:
            ServiceException: if an error occurs during browsing
        """