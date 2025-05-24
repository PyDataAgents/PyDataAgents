from abc import abstractmethod
from PyDataGrabber.adapters.Adapter import Adapter
from PyDataGrabber.buffers.Buffer import Buffer

class SubscribeAdapter(Adapter):
    """abstract class for Adapter Interface for subscribing from data sources
    """
    
    @abstractmethod
    def subscribe(self, buffers : dict[str, Buffer], addresses : list[str], sampling_period : int, n : int):
        """subscribes to data from source into specified buffers and addresses, with specified sampling_period and n samples at once
        """
    
    @abstractmethod
    def unsubscribe(self):
        """resets the subscription
        """  