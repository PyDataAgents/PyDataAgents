from abc import abstractmethod
from PyDataGrabber.src.adapters.Adapter import Adapter
from PyDataGrabber.src.buffers.Buffer import Buffer

class WriteAdapter(Adapter):
    """abstract class for Adapter Interface for writing to data sinks
    """
    
    @abstractmethod
    def write_to_sink(self, buffers : dict[str, Buffer], addresses : list[str], persistent : bool):
        pass  