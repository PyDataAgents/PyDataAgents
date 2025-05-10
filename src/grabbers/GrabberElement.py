from abc import ABC, abstractmethod
import uuid

class GrabberElement(ABC):
    """
    Abstract base class for grabber elements.
    """
    
    def __init__(self):
        """
        Initialize the grabber element and assign a unique ID.
        """
        self.id = GrabberElement.unique_id(self)
    
    @staticmethod
    def unique_id(obj):
        """
        Generate a unique ID for the grabber element.
        
        Returns:
            str: A unique identifier for the grabber element.
        """
        return f"{obj.__class__.__name__} [{uuid.uuid4()}]"
        
    def get_id(self):
        """
        Get the unique ID of the grabber element.
        
        Returns:
            str: The unique identifier for the grabber element.
        """
        return self.id
    
    def set_id(self, id):
        """
        Set the unique ID of the grabber element.
        
        Args:
            id (str): The unique identifier for the grabber element.
        """
        self.id = id
        return self