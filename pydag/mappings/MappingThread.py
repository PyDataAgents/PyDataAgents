from __future__ import annotations
from typing import TYPE_CHECKING
from loguru import logger

from ..agents.AgentElement import AgentElement
from .Mapping import Mapping
from .MappingType import MappingType
from .ObserverThread import ObserverThread
from .PublishMappingObserver import PublishMappingObserver
from .ReadMappingObserver import ReadMappingObserver
from .SubscribeMappingObserver import SubscribeMappingObserver
from .WriteMappingObserver import WriteMappingObserver

if TYPE_CHECKING:
    from pydag.agents.Agent import Agent

class MappingThread(AgentElement):
    
    def __init__(self, mapping : Mapping):
        super().__init__()
        self.mapping = mapping
    
    def __post_init__(self):
        super().__post_init__()
        self.observer_thread : ObserverThread = None
        
    def start(self, agent : Agent):
        self.observer_thread = ObserverThread(id=ObserverThread.unique_id(), thread_type=self.mapping.thread_type, sampling_period=self.mapping.sampling_period)
        # assemble adapters and buffers from agent
        if self.mapping.adapter is None and len(self.mapping.buffers) == 0:
            for buffer_id in self.mapping.buffer_ids:
                if buffer_id in agent.buffer_store:
                    self.mapping[buffer_id] = agent.buffer_store[buffer_id]
                else:
                    logger.error("Buffer " + buffer_id + " not found in agent")
            if self.mapping.adapter_id in agent.adapter_store:
                self.mapping.adapter = agent.adapter_store[self.mapping.adapter_id]
            else:
                logger.error("Adapter " + self.mapping.adapter_id + " not found in agent")        
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
        