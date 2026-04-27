from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass


from .MappingService import MappingService


@dataclass
class ReadService(MappingService):
        
    
    @abstractmethod
    def _read_from_source(self):
        """ read logic from source into buffers for specified addresses and n samples at once

        Args:
            buffers (dict[str, Buffer]): _description_
        """