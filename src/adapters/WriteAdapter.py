from abc import abstractmethod
from PyDataGrabber.src.adapters.Adapter import Adapter
from PyDataGrabber.src.buffers.Buffer import Buffer

class WriteAdapter(Adapter):
    """abstract class for Adapter Interface for writing to data sinks
    """
    
    @abstractmethod
    def write_to_sink(self, buffers : dict[str, Buffer], addresses : list[str], n : int, persistent : bool):
        """writes data from buffers to sink, based on specified addresses and n number of samples
        <br>if persistent = False, then the values are removed from buffer on writing

        Args:
            buffers (dict[str, Buffer]): _description_
            addresses (list[str]): _description_
            n (int): _description_
            persistent (bool): _description_
        """
        pass