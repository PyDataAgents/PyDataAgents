from __future__ import annotations
from typing import TYPE_CHECKING
from .Observer import Observer


if TYPE_CHECKING:
    from .MappingService import MappingService

class MappingObserver(Observer):
    """ abstract base class for mapping observers
    """
    
    def __init__(self, mapping : MappingService):
        super().__init__()
        self._mapping : MappingService = mapping               
                    
    def get_mapping(self) -> MappingService:
        return self._mapping
      