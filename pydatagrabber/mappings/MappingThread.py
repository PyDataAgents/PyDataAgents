from __future__ import annotations
from typing import TYPE_CHECKING
from ..grabbers.GrabberElement import GrabberElement
from .Mapping import Mapping
from .MappingType import MappingType
from .ObserverThread import ObserverThread
from .PublishMappingObserver import PublishMappingObserver
from .ReadMappingObserver import ReadMappingObserver
from .SubscribeMappingObserver import SubscribeMappingObserver
from .WriteMappingObserver import WriteMappingObserver

if TYPE_CHECKING:
    from pydatagrabber.grabbers.Grabber import Grabber

class MappingThread(GrabberElement):
    
    def __init__(self, mapping : Mapping):
        super().__init__()
        self.mapping : Mapping = mapping
        self.observer_thread : ObserverThread = None
        
    def start(self, grabber : Grabber):
        self.observer_thread = ObserverThread(self.observer_thread.unique_id(), self.mapping.thread_type, self.mapping.sampling_period)
        # assemble adapters and buffers from Grabber
        if self.mapping.adapter is None and len(self.mapping.buffers) == 0:
            for buffer_id in self.mapping.buffer_ids:
                if buffer_id in grabber.buffer_store:
                    self.mapping[buffer_id] = grabber.buffer_store[buffer_id]
                else:
                    self.LOGGER.error("Buffer " + buffer_id + " not found in Grabber")
            if self.mapping.adapter_id in grabber.adapter_store:
                self.mapping.adapter = grabber.adapter_store[self.mapping.adapter_id]
            else:
                self.LOGGER.error("Adapter " + self.mapping.adapter_id + " not found in Grabber")        
        # add observer to observer thread
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
        