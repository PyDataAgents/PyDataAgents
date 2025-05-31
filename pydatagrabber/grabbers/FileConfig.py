from abc import ABC, abstractmethod

from PyDataGrabber.pydatagrabber.grabbers.GrabberConfig import GrabberConfig


class FileConfig(ABC):
    """
    Abstract base class for file configuration.
    """

    def __init__(self, file_path : str):
        """
        Initialize the file configuration and assign a unique ID.
        """
        self.file_path = file_path
            
    @abstractmethod
    def load(self) -> GrabberConfig:
        pass
    
    @abstractmethod
    def save(self, grabber_config : GrabberConfig):
        pass
    