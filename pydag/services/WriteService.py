from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass


from .MappingService import MappingService


@dataclass
class WriteService(MappingService):
        
    @abstractmethod
    def _write_to_sink(self):
        """ write logic from buffers to sink for specified addresses and n samples at once

        Args:
        
        """