from PyDataGrabber.src.mappings.MappingObserver import MappingObserver
from PyDataGrabber.src.mappings.Mapping import Mapping


class ReadMappingObserver(MappingObserver):
    
    def __init__(self, mapping: Mapping, id: str = None):
        super().__init__(mapping, id)

    def observe(self):
        self.mapping.adapter.read_from_source(self.mapping.buffers, self.mapping.addresses)
    
    def unobserve(self):
        pass