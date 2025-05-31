from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass
import time
from loguru import logger
from .GrabberElement import GrabberElement
from ..mappings.MappingThread import MappingThread

if TYPE_CHECKING:
    from ..adapters.Adapter import Adapter
    from ..buffers.Buffer import Buffer
    from ..mappings.Mapping import Mapping
    from ..services.Service import Service

@dataclass
class Grabber(GrabberElement):
    
    def __init__(self):
        super().__init__()
        self.buffer_store : dict[str, Buffer] = dict()
        self.adapter_store : dict[str, Adapter] = dict()
        self.mapping_store : dict[str, MappingThread] = dict()
        self.service_store : dict[str, Service] = dict()
        self.is_running = False
    
    def install(self, grabber : Grabber = None):        
        self.install_elements()
        
    def deinstall(self, grabber : Grabber = None):
        self.deinstall_elements()
    
    def install_elements(self):
        for adapter in self.adapter_store.values():
            adapter.install(self)
        for buffer in self.buffer_store.values():
            buffer.install(self)
        for mapping in self.mapping_store.values():
            mapping.install(self)
        for service in self.service_store.values():
            service.install(self)
    
    def deinstall_elements(self):
        for adapter in self.adapter_store.values():
            adapter.deinstall(self)
        for buffer in self.buffer_store.values():
            buffer.deinstall(self)
        for mapping in self.mapping_store.values():
            mapping.deinstall(self)
        for service in self.service_store.values():
            service.deinstall(self)
            
    def add_buffer(self, buffer : Buffer):
        self.buffer_store[buffer.id] = buffer
        
    def add_adapter(self, adapter : Adapter):
        self.adapter_store[adapter.id] = adapter
        
    def add_mapping(self, mapping : Mapping):
        mapping_thread = MappingThread(mapping)
        self.mapping_store[mapping.id] = mapping_thread
        
    def add_service(self, service : Service):
        self.service_store[service.id] = service
        
    def start_blocking(self):
        self.start()
        while self.is_running:
            time.sleep(3)
    
    def start(self):
        self.install()
        self.is_running = True        
        self.connect_adapters()
        self.start_mappings()
        self.start_services()       
    
            
    def connect_adapters(self):
        for adapter in self.adapter_store.values():
            if adapter.connect() is False:
                logger.error(adapter.name() + " could not be connected")           
    
    def start_mappings(self):
        for mapping_thread in self.mapping_store.values():
            mapping_thread.start(self)
            
    def start_services(self):
        for service in self.service_store.values():
            service.start()
    
    def stop(self):
        self.is_running = False
        self.stop_services()
        self.stop_mappings()
        self.disconnect_adapters()
        
    def disconnect_adapters(self):
        for adapter in self.adapter_store.values():
            if adapter.disconnect() is False:
                logger.error(adapter.name() + " could not be disconnected")
    
    def stop_mappings(self):
        for mapping in self.mapping_store.values():
            mapping.stop()
    
    def stop_services(self):
        for service in self.service_store.values():
            service.stop()
            
    def get_adapter(self, id : str) -> Adapter:
        if id in self.adapter_store:
            return self.adapter_store[id]    
        else:
            logger.error("No " + Adapter.__class__.__name__ + " with id=" + id + " was found")
            return None
    
    def get_buffer(self, id : str) -> Buffer:
        if id in self.buffer_store:
            return self.buffer_store[id]    
        else:
            logger.error("No " + Buffer.__class__.__name__ + " with id=" + id + " was found")
            return None
    
    def get_mapping_thread(self, id : str) -> MappingThread:
        if id in self.mapping_store:
            return self.mapping_store[id]    
        else:
            logger.error("No " + MappingThread.__class__.__name__ + " with id=" + id + " was found")
            return None
        
    def get_mapping(self, id : str) -> Mapping:
        if id in self.mapping_store:
            return self.mapping_store[id].mapping    
        else:
            logger.error("No " + Mapping.__class__.__name__ + " with id=" + id + " was found")
            return None
        
    def get_service(self, id : str) -> Service:
        if id in self.service_store:
            return self.service_store[id]    
        else:
            logger.error("No " + Service.__class__.__name__ + " with id=" + id + " was found")
            return None
        
    def get_element(self, id : str) -> GrabberElement:        
        if id in self.adapter_store:
            return self.adapter_store[id]
        elif id in self.buffer_store:
            return self.buffer_store[id]
        elif id in self.mapping_store:
            return self.mapping_store[id]
        elif id in self.service_store:
            return self.service_store[id]
        else:
            return self.__get_deep_element(id)
    
    def __get_deep_element(self, id : str) -> GrabberElement:
        """checks for nested GrabberElements

        Args:
            id (str): unique id

        Returns:
            GrabberElement:
        """
        for adapter in self.adapter_store.values():
            for attr_name, attr_value in vars(adapter).items():
                #print(f"{attr_name}: {type(attr_value)}")
                if isinstance(attr_value, GrabberElement):
                    return attr_value
            for buffer in self.buffer_store.values():
                for attr_name, attr_value in vars(buffer).items():
                    #print(f"{attr_name}: {type(attr_value)}")
                    if isinstance(attr_value, GrabberElement):
                        return attr_value
        for mapping_thread in self.mapping_store.values():
            for attr_name, attr_value in vars(mapping_thread).items():
                #print(f"{attr_name}: {type(attr_value)}")
                if isinstance(attr_value, GrabberElement):
                    return attr_value
        for service in self.service_store.values():
            for attr_name, attr_value in vars(service).items():
                #print(f"{attr_name}: {type(attr_value)}")
                if isinstance(attr_value, GrabberElement):
                    return attr_value
        return None
     