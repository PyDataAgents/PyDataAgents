from PyDataGrabber.src.mappings.MappingObserver import MappingObserver

class SubscribeMappingObserver(MappingObserver):
    
    def observe(self):
        self.mapping.adapter.subscribe(self.mapping.buffers, self.mapping.addresses, self.mapping.sampling_period, self.mapping.n)
    
    def unobserve(self):
        self.mapping.adapter.unsubscribe()