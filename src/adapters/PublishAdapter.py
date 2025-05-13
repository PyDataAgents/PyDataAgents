from abc import abstractmethod
from PyDataGrabber.src.adapters.Adapter import Adapter

class PublishAdapter(Adapter):
    
    @abstractmethod
    def publish(buffers : dict, addresses : list, sampling_period : int, persistent : bool):
        pass
    
    @abstractmethod
    def unpublish():
        pass    
    