from ...adapters.Adapter import Adapter
from ..ObserverException import ObserverException
from ...adapters.AdapterException import AdapterException
from .MappingObserver import MappingObserver

class PublishMappingObserver(MappingObserver):
    
    def observe(self):
        try:
            self.get_mapping().get_adapter().publish(self.get_mapping().get_buffers(), self.get_mapping().addresses, self.get_mapping().observing_time, self.get_mapping().n, self.get_mapping().persistent)
        except AdapterException as e:
            raise ObserverException(f"Could not execute publish on {Adapter.cname()}: {self.get_mapping().get_adapter().config_options()}") from e
    
    def unobserve(self):
        self.get_mapping().get_adapter().unpublish()