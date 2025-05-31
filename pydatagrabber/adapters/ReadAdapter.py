from abc import abstractmethod
from PyDataGrabber.pydatagrabber.adapters.Adapter import Adapter
from PyDataGrabber.pydatagrabber.buffers.Buffer import Buffer

class ReadAdapter(Adapter):
    """abstract class for Adapter Interface for reading from data sources
    """
    
    @abstractmethod
    def read_from_source(self, buffers : dict[str, Buffer], addresses : list[str], n : int):
        """ reads data from source into buffers for specified addresses and n samples at once

        Args:
            buffers (dict[str, Buffer]): _description_
            addresses (list[str]): _description_
            n (int): _description_
        """    