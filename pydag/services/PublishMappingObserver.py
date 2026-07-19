from __future__ import annotations

from .PublishService import PublishService
from .ServiceException import ServiceException
from .ObserverException import ObserverException
from .MappingObserver import MappingObserver


class PublishMappingObserver(MappingObserver):
    
    def __post_init__(self):
        #self._mapping : PublishService = self._mapping
        pass
    
    def observe(self):
        try:
            if isinstance(self._mapping, PublishService):
                self._mapping.publish(self)
        except ServiceException as e:
            raise ObserverException(f"Could not execute publish on {self._mapping.__class__.__name__}:\n\t{e.message}") from e
    
    def unobserve(self):
        if isinstance(self._mapping, PublishService):
            self._mapping.unpublish()