from PyDataGrabber.src.mappings.MappingObserver import MappingObserver
from PyDataGrabber.src.mappings.Mapping import Mapping


class SubscribeMappingObserver(MappingObserver):
    
    def __init__(self, mapping: Mapping, id: str = None):
        super().__init__(mapping, id)

    def observe(self):
        self.mapping.adapter.subscribe(self.mapping.buffers, self.mapping.addresses, self.mapping.sampling_period)
    
    def unobserve(self):
        self.mapping.adapter.unsubscribe()