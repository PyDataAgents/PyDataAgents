from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement
from PyDataGrabber.src.adapters.Adapter import Adapter
from PyDataGrabber.src.buffers.Buffer import Buffer
from PyDataGrabber.src.mappings.MappingType import MappingType
from PyDataGrabber.src.mappings.ThreadType import ThreadType


class Mapping(GrabberElement):
    """_summary_

    Args:
        GrabberElement (_type_): _description_
    """

    def __init__(self, id : str = None):
        super().__init__(id)
        self.buffers : dict[Buffer] = dict()
        self.adapter : Adapter = None
        self.addresses : list[str] = None
        self.thread_type : ThreadType = ThreadType.MILLI_SECOND
        self.sampling_period : int = 0
        self.n : int = 1
        self.mapping_type : MappingType = None
        self.persistent = True