from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union
from loguru import logger


from ..ObserverException import ObserverException
from ..ServiceException import ServiceException
from ...agents.AgentStates import AgentElementState
from ..ThreadType import ThreadType
from ..MappingService import MappingService
from ..Observer import Observer
from ...agents.Agent import Agent
from ..ObserverService import ObserverService


class RestartObserver(Observer):
    """ Observer for checking restart attempts of other `MappingServices`'s
    """
    
    def __init__(self, service : MappingRestartService):
        self._service : MappingRestartService = service
        
    def observe(self):
        for service in self._service.get_agent().service_store.values():
            if isinstance(service, MappingService):
                requires_restart : bool = False
                if service.get_state() == AgentElementState.ERROR:
                    if service.id in self._service.get_restart_attempts():
                        ra = self._service.get_restart_attempts()[service.id]
                        if ra < self._service.max_restart_attempts:
                            requires_restart = True
                    else:
                        requires_restart = True
                if requires_restart:
                    try:
                        service.stop() # stop the service to prepare for restart
                        #service.uninstall() # uninstall before install
                        service.install() # reinstall the service to reset it
                        service.start() # start the service to trigger the restart
                        self._service.get_restart_attempts().pop(service.id, None)
                    except ServiceException as e:
                        # keep the error state
                        service.set_state(AgentElementState.ERROR)
                        # increment the restart count
                        if service.id in self._service.get_restart_attempts():
                            self._service.get_restart_attempts()[service.id] = self._service.get_restart_attempts()[service.id] + 1
                        else:
                            self._service.get_restart_attempts()[service.id] = 1
                        logger.debug(f"Failed to restart {service.__class__.__name__} {service.id}, attempt {self._service.get_restart_attempts()[service.id]}: {e}")
    
    def unobserve(self):
        self._service.get_restart_attempts().clear()

@dataclass
class MappingRestartService(ObserverService):
    """ An `ObserverService` that attempts restarts on failed `MappingService`'s

    Args:
        ObserverService (Service): parent class
    """

    thread_type : str = field(default=ThreadType.SECOND, metadata={"description": "type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ..."})    
    observing_time : Union[int|str] = field(default=10, metadata={"description": "interval of seconds for restarts attempts"})
    max_restart_attempts : int = field(default=3, metadata={"description": "number of consecutive restarts attempts before omitting the mapping service from restart attempts"})
    
    def __post_init__(self):
        super().__post_init__()
        self._restart_attempts : dict[str, int] = dict()        
            
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        observer : RestartObserver = RestartObserver(self)
        self.add_observer(observer)
        
    def get_restart_attempts(self) -> dict[str, int]:
        return self._restart_attempts