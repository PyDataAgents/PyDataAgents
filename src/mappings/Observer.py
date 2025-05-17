from abc import abstractmethod
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement


class Observer(GrabberElement):
    
    def __init__(self, id : str = None):
        super().__init__(id)
        
    @abstractmethod
    def observe(self):
        pass
    
    @abstractmethod
    def unobserve(self):
        pass
        

    