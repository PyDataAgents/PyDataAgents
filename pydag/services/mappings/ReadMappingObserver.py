from .MappingObserver import MappingObserver

class ReadMappingObserver(MappingObserver):
    def observe(self):
        self.get_mapping().get_adapter().read_from_source(self.get_mapping().get_buffers(), self.get_mapping().addresses, self.get_mapping().n)
    
    def unobserve(self):
        pass