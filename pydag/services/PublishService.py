from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass


from .MappingService import MappingService


@dataclass
class PublishService(MappingService):
    
    @abstractmethod
    def publish(self):
        """publish samples from buffers to addresses with specified sampling_period and n samples at once
            <br>if persistent is specified False, then the samples will be removed from buffers

        Args:
        
        Raises:
            ServiceException: if an error occurs during publishing
        """        
    
    @abstractmethod
    def unpublish(self):
        """ unpublish logic to stop publishing
        
        Raises:
            ServiceException: if an error occurs during unpublishing
        """