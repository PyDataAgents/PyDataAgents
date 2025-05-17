from PyDataGrabber.src.mappings.MappingObserver import MappingObserver
from PyDataGrabber.src.mappings.Mapping import Mapping


class PublishMappingObserver(MappingObserver):
    
    def __init__(self, mapping: Mapping, id: str = None):
        super().__init__(mapping, id)

    def observe(self):
        self.mapping.adapter.publish(self.mapping.buffers, self.mapping.addresses, self.mapping.sampling_period, self.mapping.persistent)
    
    def unobserve(self):
        self.mapping.adapter.unpublish()