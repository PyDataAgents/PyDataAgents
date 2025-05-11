from abc import ABC, abstractmethod
import uuid

from loguru import logger

class GrabberElement(ABC):
    """
    Abstract base class for grabber elements.
    """

    LOGGER = logger
    
    def __init__(self, id: str = None):
        """
        Initialize the grabber element and assign a unique ID.
        """
        self.type = self.__module__
        if id == None:
            self.id = GrabberElement.unique_id(self)        
    
    @staticmethod
    def unique_id(obj):
        """
        Generate a unique ID for the grabber element.
        
        Returns:
            str: A unique identifier for the grabber element.
        """
        return f"{obj.__class__.__name__} [{uuid.uuid4()}]"
        
    def config_options(self) -> dict:
        d = dict()
        d["type"] = self.type
        d["id"] = self.id
        return d