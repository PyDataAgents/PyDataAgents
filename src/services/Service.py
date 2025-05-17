from abc import abstractmethod
from PyDataGrabber.src.grabbers.Grabber import Grabber
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement


class Service(GrabberElement):
    
    def __init__(self, id):
        super().__init__(id)
        self.grabber : Grabber = None
        self.is_running : bool = False
        
    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass
    
    def grabber(self, grabber : Grabber):
        self.grabber = grabber
    
    