from loguru import logger

from ..ObserverException import ObserverException
from ...adapters.AdapterException import AdapterException
from ...agents.AgentStates import AgentElementState, ServiceState
from .MappingObserver import MappingObserver

class SubscribeMappingObserver(MappingObserver):
    
    def observe(self):
        try:
            self._mapping.get_adapter().subscribe(self._mapping.get_buffers(), self._mapping.addresses, self._mapping.observing_time, self._mapping.n, self.mapping_error_callback)
        except AdapterException as e:
            raise ObserverException(f"Could not execute subscribe on {self._mapping.get_adapter().cname()}: {self._mapping.get_adapter().config_options()}") from e

    def unobserve(self):
        self._mapping.get_adapter().unsubscribe()
        self._mapping.set_state(ServiceState.STOPPED)
        
    def mapping_error_callback(self, e : Exception):
        """ this callback is used in subscribe calls to retrieve back subscription errors back to the mapping service

        Args:
            e (Exception): _description_
        """
        self._mapping.set_state(AgentElementState.ERROR)
        logger.error(e)