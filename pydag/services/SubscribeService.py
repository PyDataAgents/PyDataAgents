from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass


from .MappingService import MappingService


@dataclass
class SubscribeService(MappingService):
    
    @abstractmethod
    def _subscribe(self):
        """subscribe logic from source into specified buffers and addresses, with specified sampling_period and n samples at once
        
        Args:
            
        """
    
    @abstractmethod
    def _unsubscribe(self):
        """ unsubscribe logic to stop subscribing
        """