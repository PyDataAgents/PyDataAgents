from PyDataGrabber.src.mappings.MappingObserver import MappingObserver

class ReadMappingObserver(MappingObserver):
    def observe(self):
        self.mapping.adapter.read_from_source(self.mapping.buffers, self.mapping.addresses, self.mapping.n)
    
    def unobserve(self):
        pass