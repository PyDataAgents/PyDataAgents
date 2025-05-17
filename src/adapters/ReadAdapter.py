from abc import abstractmethod
from PyDataGrabber.src.adapters.Adapter import Adapter
from PyDataGrabber.src.buffers.Buffer import Buffer

class ReadAdapter(Adapter):
    """abstract class for Adapter Interface for reading from data sources
    """
    
    @abstractmethod
    def read_from_source(self, buffers : dict[str, Buffer], addresses : list[str]):
        pass    