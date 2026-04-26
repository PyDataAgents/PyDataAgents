from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union


from ...agents.AgentStates import AgentElementState
from ..ThreadType import ThreadType
from ..mappings.MappingService import MappingService
from ..Observer import Observer
from ...agents.Agent import Agent
from ..ObserverService import ObserverService


class RestartObserver(Observer):
    
    def __init__(self, service : MappingRestartService):
        self._service : MappingRestartService = service
        
    def observe(self):
        for service in self._service.get_agent().service_store.values():
            if isinstance(service, MappingService):
                requires_restart : bool = False
                if service.get_state() == AgentElementState.ERROR:
                    if service.id in self._service._mapping_restarts:
                        ra = self._service._mapping_restarts[service.id]
                        if ra < self._service.restart_attempts:
                            requires_restart = True
                    else:
                        requires_restart = True
                if requires_restart:
                    if service.start():
                        self._service._mapping_restarts.pop(service.id, None)
    
    def unobserve(self):
        return

@dataclass
class MappingRestartService(ObserverService):
    """ An `ObserverService` that attempts restarts on failed `MappingService`'s

    Args:
        ObserverService (Service): parent class
    """

    thread_type : str = field(default=ThreadType.SECOND, metadata={"description": "type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ..."})    
    observing_time : Union[int|str] = field(default=10, metadata={"description": "interval of seconds for restarts attempts"})
    restart_attempts : int = field(default=3, metadata={"description": "number of consecutive restarts attempts before omitting the mapping service from restart attempts"})
    
    def __post_init__(self):
        super().__post_init__()
        self._mapping_restarts : dict = dict()        
            
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        observer : RestartObserver = RestartObserver(self)
        self._observer_thread.add_observer(observer)