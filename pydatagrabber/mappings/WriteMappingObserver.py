from PyDataGrabber.pydatagrabber.mappings.MappingObserver import MappingObserver

class WriteMappingObserver(MappingObserver):

    def observe(self):
        self.mapping.adapter.write_to_sink(self.mapping.buffers, self.mapping.addresses, self.mapping.n, self.mapping.persistent)

    def unobserve(self):
        pass