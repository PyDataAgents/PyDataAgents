from abc import abstractmethod
from PyDataGrabber.src.adapters.Adapter import Adapter

class ReadAdapter(Adapter):
    
    @abstractmethod
    def readFromSource(self, buffers : dict, addresses : list):
        pass    