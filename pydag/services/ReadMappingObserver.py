from .ServiceException import ServiceException
from .ReadService import ReadService
from .ObserverException import ObserverException
from .MappingObserver import MappingObserver

class ReadMappingObserver(MappingObserver):
    """ `MappingObserver` for reading from sources

    Args:
        MappingObserver (class): parent class
    """
    
    def __post_init__(self):
        #self._mapping : ReadService = self._mapping
        pass

    def observe(self):
        try:
            if isinstance(self._mapping, ReadService):
                self._mapping.read_from_source()
        except ServiceException as e:
            raise ObserverException(f"Could not execute read_from_source on {self._mapping.__class__.__name__}:\n\t{e.message}") from e
    
    def unobserve(self):
        pass