from __future__ import annotations
from abc import abstractmethod
from ..grabbers.Grabber import Grabber
from ..grabbers.GrabberElement import GrabberElement

class Service(GrabberElement):
    """abstract base class for Grabber Services
    """
    
    def __init__(self):
        super().__init__()
        self.is_running : bool = False
        self.grabber : Grabber = None
    
    def install(self, grabber : Grabber = None):
        super().install(grabber)
        self.grabber = grabber
        
    @abstractmethod
    def start(self):
        self.is_running = True
    
    @abstractmethod
    def stop(self):
        self.is_running = False
    
    
    