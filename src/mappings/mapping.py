
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement
from PyDataGrabber.src.adapters.Adapter import Adapter
from PyDataGrabber.src.buffers.Buffer import Buffer
from PyDataGrabber.src.mappings.MappingType import MappingType
from PyDataGrabber.src.mappings.ThreadType import ThreadType
from PyDataGrabber.src.mappings.ObserverThread import ObserverThread
from PyDataGrabber.src.mappings.PublishMappingObserver import PublishMappingObserver
from PyDataGrabber.src.mappings.ReadMappingObserver import ReadMappingObserver
from PyDataGrabber.src.mappings.SubscribeMappingObserver import SubscribeMappingObserver
from PyDataGrabber.src.mappings.WriteMappingObserver import WriteMappingObserver


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
        self.observer_thread : ObserverThread = None

    def start(self):
        self.observer_thread = ObserverThread(self.thread_type, self.sampling_period)
        match self.mapping_type:
            case MappingType.READ:
                observer = ReadMappingObserver(self)
                self.observer_thread.add_observer(observer)
            case MappingType.WRITE:
                observer = WriteMappingObserver(self)
                self.observer_thread.add_observer(observer)
            case MappingType.SUB:
                observer = SubscribeMappingObserver(self)
                self.observer_thread.add_observer(observer)
            case MappingType.PUB:
                observer = PublishMappingObserver(self)
                self.observer_thread.add_observer(observer)
        self.observer_thread.start()

    def stop(self):
        """stops the mapping
        """
        self.observer_thread.stop()
