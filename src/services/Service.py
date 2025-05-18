from abc import abstractmethod
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement


class Service(GrabberElement):
    
    def __init__(self, id):
        super().__init__(id)
        self.is_running : bool = False
        
    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass
    
    