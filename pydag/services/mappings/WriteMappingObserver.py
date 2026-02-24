from .MappingObserver import MappingObserver

class WriteMappingObserver(MappingObserver):

    def observe(self):
        self.get_mapping().get_adapter().write_to_sink(self.get_mapping().get_buffers(), self.get_mapping().addresses, self.get_mapping().n, self.get_mapping().persistent)

    def unobserve(self):
        pass