from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class LogEntry:
    timestamp : str
    level : str
    message : str
    thread : str
    
@dataclass    
class LogStore():
    
    @abstractmethod
    def add(self, entry : LogEntry):
        """ adds a new log entry to store """
        
    @abstractmethod
    def query(self, text : str = None, level : str = None, limit : int = None, thread : str = None):
        """ queries a number of log entries based on text, level, thread and given limit """
        
    @abstractmethod
    def get_thread_names(self) -> list[str]:
        """ returns the available thread names in log store """