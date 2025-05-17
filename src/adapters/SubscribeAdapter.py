from abc import abstractmethod
from PyDataGrabber.src.adapters.Adapter import Adapter
from PyDataGrabber.src.buffers.Buffer import Buffer

class SubscribeAdapter(Adapter):
    """abstract class for Adapter Interface for subscribing from data sources
    """
    
    @abstractmethod
    def subscribe(buffers : dict[str, Buffer], addresses : list[str], sampling_period : int, n : int):
        """subscribes to data from source into specified buffers and addresses, with specified sampling_period and n samples at once
        """
        pass
    
    @abstractmethod
    def unsubscribe():
        """resets the subscription
        """
        pass  