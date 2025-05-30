from __future__ import annotations
from abc import abstractmethod
from PyDataGrabber.grabbers.Grabber import Grabber
from PyDataGrabber.grabbers.GrabberElement import GrabberElement

class Service(GrabberElement):
    """abstract base class for Grabber Services
    """
    
    def __init__(self):
        super().__init__()
        self.is_running : bool = False
        self.grabber : Grabber = None
    
    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass
    
    def set_grabber(self, grabber : Grabber):
        self.grabber = grabber
    
    