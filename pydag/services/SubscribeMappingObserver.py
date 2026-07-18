from .SubscribeService import SubscribeService
from .ServiceException import ServiceException
from .ObserverException import ObserverException
from .MappingObserver import MappingObserver

class SubscribeMappingObserver(MappingObserver):
    
    def __post_init__(self):
        #self._mapping : SubscribeService = self._mapping
        pass

    def observe(self):
        try:
            if isinstance(self._mapping, SubscribeService):
                self._mapping.subscribe()
        except ServiceException as e:
            raise ObserverException(f"Could not execute subscribe on {self._mapping.__class__.__name__}:\n\t{e.message}") from e

    def unobserve(self):
        if isinstance(self._mapping, SubscribeService):
            self._mapping.unsubscribe()    