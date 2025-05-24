from dataclasses import dataclass, field
from PyDataGrabber.grabbers.GrabberElement import GrabberElement
from PyDataGrabber.adapters.Adapter import Adapter
from PyDataGrabber.buffers.Buffer import Buffer
from PyDataGrabber.mappings.ThreadType import ThreadType

@dataclass
class Mapping(GrabberElement):
    """_summary_

    Args:
        GrabberElement (_type_): _description_
    """
    
    buffer_ids : list[str] = field(default=None, metadata={"description": "list of buffer ids to map from"})
    adapter_id : str = field(default=None, metadata={"description": "id of the Adapter used for this Mapping"})
    addresses : list[str] = field(default=None, metadata={"description": "list of addresses to read/subscribe from or write/publish to"})
    thread_type : str = field(default=ThreadType.MILLI_SECOND.value, metadata={"description": "type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, ..."})
    mapping_type : str = field(default=None, metadata={"description": "type of mapping, e.g. READ, WRITE, SUB or PUB"})
    n : int = field(default=1, metadata={"description": "number of samples to insert or remove from buffers"})
    sampling_period : int = field(default=100, metadata={"description": "sampling period to apply in this Mapping"})
    persistent : bool = field(default=True, metadata={"description": "specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink"})
    
    def __init__(self):
        super().__init__()
        self.buffers : dict[Buffer] = dict()
        self.adapter : Adapter = None