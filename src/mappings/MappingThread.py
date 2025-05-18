from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement
from PyDataGrabber.src.mappings.Mapping import Mapping
from PyDataGrabber.src.mappings.MappingType import MappingType
from PyDataGrabber.src.mappings.ObserverThread import ObserverThread
from PyDataGrabber.src.mappings.PublishMappingObserver import PublishMappingObserver
from PyDataGrabber.src.mappings.ReadMappingObserver import ReadMappingObserver
from PyDataGrabber.src.mappings.SubscribeMappingObserver import SubscribeMappingObserver
from PyDataGrabber.src.mappings.WriteMappingObserver import WriteMappingObserver


class MappingThread(GrabberElement):
    
    def __init__(self, mapping : Mapping):
        super().__init__()
        self.mapping = mapping
        self.observer_thread : ObserverThread = None
    
    def start(self):
        self.observer_thread = ObserverThread(self.observer_thread.unique_id(), self.mapping.thread_type, self.mapping.sampling_period)
        match self.mapping.mapping_type:
            case MappingType.READ:
                observer = ReadMappingObserver(self.mapping)
                self.observer_thread.add_observer(observer)
            case MappingType.WRITE:
                observer = WriteMappingObserver(self.mapping)
                self.observer_thread.add_observer(observer)
            case MappingType.SUB:
                observer = SubscribeMappingObserver(self.mapping)
                self.observer_thread.add_observer(observer)
            case MappingType.PUB:
                observer = PublishMappingObserver(self.mapping)
                self.observer_thread.add_observer(observer)
        self.observer_thread.start()
        
    def stop(self):
        self.observer_thread.stop()
        