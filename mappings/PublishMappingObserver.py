from PyDataGrabber.mappings.MappingObserver import MappingObserver

class PublishMappingObserver(MappingObserver):
    
    def observe(self):
        self.mapping.adapter.publish(self.mapping.buffers, self.mapping.addresses, self.mapping.sampling_period, self.mapping.n, self.mapping.persistent)
    
    def unobserve(self):
        self.mapping.adapter.unpublish()