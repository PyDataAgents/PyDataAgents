import enum
from PyDataGrabber.src.adapters.Adapter import Adapter
from PyDataGrabber.src.buffers.Buffer import Buffer
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement
from PyDataGrabber.src.mappings.ObserverThread import ObserverThread
from PyDataGrabber.src.mappings.PublishMappingObserver import PublishMappingObserver
from PyDataGrabber.src.mappings.ReadMappingObserver import ReadMappingObserver
from PyDataGrabber.src.mappings.SubscribeMappingObserver import SubscribeMappingObserver
from PyDataGrabber.src.mappings.WriteMappingObserver import WriteMappingObserver

class ThreadType(enum.Enum):
    MILLI_SECOND = "MILLI_SECOND"
    MICRO_SECOND = "MICRO_SECOND"
    NANO_SECOND = "NANO_SECOND"
    INSTANT = "INSTANT"
    SECOND = "SECOND"
    ONLY_ONCE = "ONLY_ONCE"
    TRIGGERED = "TRIGGERED"

class MappingType(enum.Enum):
    READ = "READ"
    WRITE = "WRITE"
    SUB = "SUB"
    PUB = "PUB"

class Mapping(GrabberElement):
    
    def __init__(self, id):
        super().__init__(id)
        self.buffers : dict[Buffer] = {}
        self.adapter : Adapter = None
        self.addresses : list[str] = None
        self.thread_type : ThreadType = ThreadType.MILLI_SECOND
        self.sampling_period : int = 0
        self.n : int = 1
        self.mapping_type : MappingType = None
        self.persistent = True
        self.observer_thread : ObserverThread = None

    def thread_type(self, thread_type = ThreadType.MILLI_SECOND):
        self.thread_type = thread_type
        return self

    def buffer(self, buffer: Buffer):
        self.buffers.update(buffer.id, buffer)
        return self

    def buffers(self, buffers: dict):
        self.buffers = buffers
        return self

    def address(self, address: str):
        self.addresses.append(address)
        return self

    def addresses(self, addresses: list):
        self.addresses = addresses
        return self 

    def adapter(self, adapter: Adapter):
        self.adapter = adapter
        return self

    def sampling_period(self, sampling_period : int):
        self.sampling_period = sampling_period
        return self 
    
    def n(self, n : int):
        self.n = n
        return self
    
    def persistent(self, persistent : bool = True):
        self.persistent = persistent
        return self
    
    def mapping_type(self, mapping_type : MappingType):
        self.mapping_type = mapping_type
        return self
    
    def start(self):
        self.observer_thread = ObserverThread(self.thread_type)
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
        
        
    