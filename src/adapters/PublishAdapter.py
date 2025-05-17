from abc import abstractmethod
from PyDataGrabber.src.adapters.Adapter import Adapter
from PyDataGrabber.src.buffers.Buffer import Buffer

class PublishAdapter(Adapter):
    """abstract class for Adapter Interface for publishing to data sinks
    """
    
    @abstractmethod
    def publish(buffers : dict[str, Buffer], addresses : list[str], sampling_period : int, n : int, persistent : bool):
        """publish samples from buffers to addresses with specified sampling_period and n samples at once
            <br>if persistent is specified False, then the samples will be removed from buffers

        Args:
            buffers (dict[str, Buffer]): _description_
            addresses (list[str]): _description_
            sampling_period (int): _description_
            n (int): _description_
            persistent (bool): _description_
        """
        pass
    
    @abstractmethod
    def unpublish():
        """ resets the adapter to stop publishing
        """
        pass    
    