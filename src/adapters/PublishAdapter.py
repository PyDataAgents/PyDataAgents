from abc import abstractmethod
from PyDataGrabber.src.adapters.Adapter import Adapter
from PyDataGrabber.src.buffers.Buffer import Buffer

class PublishAdapter(Adapter):
    """abstract class for Adapter Interface for publishing to data sinks
    """
    
    @abstractmethod
    def publish(buffers : dict[str, Buffer], addresses : list[str], sampling_period : int, persistent : bool):
        pass
    
    @abstractmethod
    def unpublish():
        pass    
    