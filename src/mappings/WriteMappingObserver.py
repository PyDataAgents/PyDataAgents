from PyDataGrabber.src.mappings.MappingObserver import MappingObserver
from PyDataGrabber.src.mappings.Mapping import Mapping


class WriteMappingObserver(MappingObserver):

    def __init__(self, mapping: Mapping, id: str = None):
        super().__init__(mapping, id)

    def observe(self):
        self.mapping.adapter.write_to_sink(self.mapping.buffers, self.mapping.addresses, self.mapping.n, self.mapping.persistent)

    def unobserve(self):
        pass