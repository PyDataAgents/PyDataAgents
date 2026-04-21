from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union


from ...agents.AgentStates import AgentElementState
from ...services.ThreadType import ThreadType
from ...services.mappings.MappingService import MappingService
from ...services.Observer import Observer
from ...agents.Agent import Agent
from ..ObserverService import ObserverService


class ReconnectObserver(Observer):
    
    def __init__(self, service : MappingReconnectService):
        self._service : MappingReconnectService = service
        
    def observe(self):
        for service in self._service.get_agent().service_store.values():
            if isinstance(service, MappingService):
                requires_reconnect : bool = False
                if service.get_state() == AgentElementState.ERROR:
                    if service.id in self._service._mapping_reconnects:
                        ra = self._service._mapping_reconnects[service.id]
                        if ra < self._service.reconnect_attempts:
                            requires_reconnect = True
                    else:
                        requires_reconnect = True
                if requires_reconnect:
                    if service.get_adapter().connect():
                        self._service._mapping_reconnects.pop(service.id, None)
    
    def unobserve(self):
        return

@dataclass
class MappingReconnectService(ObserverService):
    """ An `ObserverService` that attempts reconnects on failed `MappingService`'s

    Args:
        ObserverService (Service): parent class
    """

    thread_type : str = field(default=ThreadType.SECOND, metadata={"description": "type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ..."})    
    observing_time : Union[int|str] = field(default=10, metadata={"description": "interval of seconds for reconnect attempts"})
    reconnect_attempts : int = field(default=3, metadata={"description": "number of consecutive reconnect attempts before omitting the mapping service from reconnect attempts"})
    
    def __post_init__(self):
        super().__post_init__()
        self._mapping_reconnects : dict = dict()        
            
    def _on_install(self, agent : Agent = None):
        super()._on_install()
        observer : ReconnectObserver = ReconnectObserver(self)
        self._observer_thread.add_observer(observer)