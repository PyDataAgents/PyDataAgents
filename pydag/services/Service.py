from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Union
from loguru import logger


from .ServiceException import ServiceException
from ..agents.AgentStates import AgentElementState, ServiceState
from ..agents.AgentElement import AgentElement


if TYPE_CHECKING:
    from ..agents.Agent import Agent

@dataclass
class Service(AgentElement):
    """abstract base class for agent Services
    """
    
    auto_start : bool = field(default=True, metadata={"description": "specifies whether to start the mapping with agent start"})
        
    def __post_init__(self):
        super().__post_init__()
        self._agent : "Agent" = None
        self._state : Union[ServiceState, AgentElementState] = AgentElementState.UNINSTALLED
    
    def _on_install(self, agent : "Agent" = None):
        self._agent = agent        
    
    def _on_uninstall(self, agent : "Agent" = None):
        self._agent : None
    
    def start(self):
        """Start the service and mark it as running.

        Implementations should perform any startup tasks required by the service.
        
        Raises:
            ServiceException: if this `Service` cannot be started
        """
        try:
            self._check_state(ServiceState.RUNNING)
            self._state = ServiceState.RUNNING        
            self._on_start()
        except ServiceException as e:
            self._state = AgentElementState.ERROR
            raise ServiceException(f"Could not start {self.__class__.__name__}") from e
    
    @abstractmethod
    def _on_start(self):
        """ start up logic called when the service is started.
        Implementations should perform any additional startup tasks required by the
        service.
        this method must be implemented with non-blocking behavior
        
        Raises:
            ServiceException: if this `Service` cannot be started
        """      
    
    def stop(self):
        """Stop the service and mark it as not running.

        Implementations should perform any cleanup and shutdown tasks required by the
        service. Subclasses shall call `super().stop()` to ensure the internal
        `_is_running` flag is cleared (set to False) once the service has stopped.
        """
        self._check_state(ServiceState.INSTALLED)
        self._on_stop()
        self._state = ServiceState.INSTALLED
        
    
    @abstractmethod
    def _on_stop(self):
        """ shutdown logic called when the service is stopped.
        Implementations should perform any additional shutdown tasks required by the
        service.
        """
        
    def _check_state(self, next_state : AgentElementState):
        match(next_state):
            case AgentElementState.UNINSTALLED:
                if self._state == ServiceState.RUNNING:
                    raise ServiceException(f"{Service.__name__} {self.id} cannot be running when uninstalling!")
                
            case AgentElementState.INSTALLED:
                if self._state == ServiceState.RUNNING:
                    raise ServiceException(f"{Service.__name__} {self.id} cannot be running when installing!")
                
            case AgentElementState.ERROR:
                # any prior state is allowed
                return
            
            case ServiceState.RUNNING:
                if self._state != ServiceState.INSTALLED:
                    raise ServiceException(f"{Service.__name__} {self.id} must be installed before starting!")
                
    def get_agent(self) -> Agent:
        """ returns the `Agent`

        Returns:
            Agent: the application's `Agent`
        """
        return self._agent 