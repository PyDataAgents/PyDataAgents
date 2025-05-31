from abc import abstractmethod
from PyDataGrabber.pydatagrabber.grabbers.GrabberElement import GrabberElement


class Observer(GrabberElement):
    
    def __init__(self):
        super().__init__()
                
    @abstractmethod
    def observe(self):
        pass
    
    @abstractmethod
    def unobserve(self):
        pass
        

    