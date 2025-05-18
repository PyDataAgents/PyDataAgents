from __future__ import annotations
from typing import TYPE_CHECKING
from abc import abstractmethod
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement

if TYPE_CHECKING:
    from PyDataGrabber.src.grabbers.Grabber import Grabber

class Service(GrabberElement):
    
    def __init__(self, id):
        super().__init__(id)
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
    
    