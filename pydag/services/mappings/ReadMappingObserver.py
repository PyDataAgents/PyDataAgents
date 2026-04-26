from ..ObserverException import ObserverException
from ...adapters.AdapterException import AdapterException
from .MappingObserver import MappingObserver

class ReadMappingObserver(MappingObserver):
    
    def observe(self):
        try:
            self.get_mapping().get_adapter().read_from_source(self.get_mapping().get_buffers(), self.get_mapping().addresses, self.get_mapping().n)
        except AdapterException as e:
            raise ObserverException(f"Could not execute read_from_source on {self.get_mapping().get_adapter().cname()}: {self.get_mapping().get_adapter().config_options()}") from e
    
    def unobserve(self):
        pass