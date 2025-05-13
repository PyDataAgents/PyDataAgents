from abc import abstractmethod
from PyDataGrabber.src.adapters.Adapter import Adapter

class WriteAdapter(Adapter):
    
    @abstractmethod
    def writeToSink(self, buffers : dict, addresses : list, persistent : bool):
        pass  