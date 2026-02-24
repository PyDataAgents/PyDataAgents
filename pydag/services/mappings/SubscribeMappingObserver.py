from .MappingObserver import MappingObserver

class SubscribeMappingObserver(MappingObserver):
    
    def observe(self):
        self._mapping.get_adapter().subscribe(self._mapping.get_buffers(), self._mapping.addresses, self._mapping.observing_time, self._mapping.n)
    
    def unobserve(self):
        self._mapping.get_adapter().unsubscribe()