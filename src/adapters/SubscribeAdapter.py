from abc import abstractmethod
from PyDataGrabber.src.adapters.Adapter import Adapter

class SubscribeAdapter(Adapter):
    
    @abstractmethod
    def subscribe(buffers : dict, addresses : list, sampling_period : int):
        pass
    
    @abstractmethod
    def unsubscribe():
        pass  