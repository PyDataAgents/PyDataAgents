from .ServiceException import ServiceException
#from .WriteService import WriteService
from .ObserverException import ObserverException
from .MappingObserver import MappingObserver


class WriteMappingObserver(MappingObserver):
    """ `MappingObserver` for writing to sinks

    Args:
        MappingObserver (_type_): _description_
    """
    
    def __post_init__(self):
        #self._mapping : WriteService = self._mapping
        pass

    def observe(self):
        try:
            self._mapping._write_to_sink()
        except ServiceException as e:
            raise ObserverException(f"Could not execute write_to_sink on {self._mapping.__class__.__name__}: {self._mapping.config_options()}") from e

    def unobserve(self):
        pass