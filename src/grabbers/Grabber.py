import time
from PyDataGrabber.src.adapters.Adapter import Adapter
from PyDataGrabber.src.buffers.Buffer import Buffer
from PyDataGrabber.src.grabbers.GrabberElement import GrabberElement
from PyDataGrabber.src.mappings.Mapping import Mapping
from PyDataGrabber.src.services.Service import Service


class Grabber(GrabberElement):
    
    def __init__(self, id : str = None):
        super().__init__(id)
        self.buffer_store : dict[Buffer] = dict()
        self.adapter_store : dict[Adapter] = dict()
        self.mapping_store : dict[Mapping] = dict()
        self.service_store : dict[Service] = dict()
        self.isRunning = False
    
    def add_buffer(self, buffer : Buffer):
        self.buffer_store[buffer.id] = buffer
        
    def add_adapter(self, adapter : Adapter):
        self.adapter_store[adapter.id] = adapter
        
    def add_mapping(self, mapping : Mapping):
        self.mapping_store[mapping.id] = mapping
        
    def add_service(self, service : Service):
        self.service_store[service.id] = service
        
    def start_blocking(self):        
        self.start()
        while self.isRunning:
            time.sleep(3)            
    
    def start(self):
        self.isRunning = True
        self.connect_adapters()
        self.start_mappings()
        self.start_services()       
    
    def connect_adapters(self):
        for adapter in self.adapter_store:
            if adapter.connect() == False:
                Grabber.LOGGER.error(adapter.name() + " could not be connected")                
    
    def start_mappings(self):
        for mapping in self.mapping_store:
            mapping.start()
            
    def start_services(self):
        for service in self.service_store:
            service.start()
    
    def stop(self):
        self.isRunning = False
        self.stop_services()
        self.stop_mappings()
        self.disconnect_adapters()
        
    def disconnect_adapters(self):
        for adapter in self.adapter_store:
            if adapter.disconnect() == False:
                Grabber.LOGGER.error(adapter.name() + " could not be disconnected")
    
    def stop_mappings(self):
        for mapping in self.mapping_store:
            mapping.stop()
    
    def stop_services(self):
        for service in self.service_store:
            service.stop()
            
    def get_adapter(self, id : str) -> Adapter:
        if id in self.adapter_store:
            return self.adapter_store[id]    
        else:
            Grabber.LOGGER.error("No " + Adapter.__class__.__name__ + " with id=" + id + " was found")
            return None
    
    def get_buffer(self, id : str) -> Buffer:
        if id in self.buffer_store:
            return self.buffer_store[id]    
        else:
            Grabber.LOGGER.error("No " + Buffer.__class__.__name__ + " with id=" + id + " was found")
            return None
        
    def get_mapping(self, id : str) -> Mapping:
        if id in self.mapping_store:
            return self.mapping_store[id]    
        else:
            Grabber.LOGGER.error("No " + Mapping.__class__.__name__ + " with id=" + id + " was found")
            return None
        
    def get_service(self, id : str) -> Service:
        if id in self.service_store:
            return self.service_store[id]    
        else:
            Grabber.LOGGER.error("No " + Service.__class__.__name__ + " with id=" + id + " was found")
            return None
    
            
    