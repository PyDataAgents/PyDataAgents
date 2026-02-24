from abc import ABC, abstractmethod

from .AgentConfig import AgentConfig


class FileConfig(ABC):
    """
    Abstract base class for file configuration.
    """

    def __init__(self, file_path : str):
        """
        Initialize the file configuration and assign a unique ID.
        """
        self._file_path = file_path
            
    @abstractmethod
    def load(self) -> AgentConfig:
        pass
    
    @abstractmethod
    def save(self, agent_config : AgentConfig):
        pass
    