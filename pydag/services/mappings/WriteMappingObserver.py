from ...adapters.AdapterException import AdapterException
from ..ObserverException import ObserverException

from .MappingObserver import MappingObserver

class WriteMappingObserver(MappingObserver):

    def observe(self):
        try:
            self.get_mapping().get_adapter().write_to_sink(self.get_mapping().get_buffers(), self.get_mapping().addresses, self.get_mapping().n, self.get_mapping().persistent)
        except AdapterException as e:
            raise ObserverException(f"Could not execute write_to_sink on {self.get_mapping().get_adapter().cname()}: {self.get_mapping().get_adapter().config_options()}") from e

    def unobserve(self):
        pass