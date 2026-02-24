from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Union


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
        """
        self._state = ServiceState.RUNNING
        self._on_start()
    
    @abstractmethod
    def _on_start(self):
        """ start up logic called when the service is started.
        Implementations should perform any additional startup tasks required by the
        service.
        this method must be implemented with non-blocking behavior
        """      
    
    def stop(self):
        """Stop the service and mark it as not running.

        Implementations should perform any cleanup and shutdown tasks required by the
        service. Subclasses shall call `super().stop()` to ensure the internal
        `_is_running` flag is cleared (set to False) once the service has stopped.
        """
        self._on_stop()
        self._state = ServiceState.STOPPED
        
    
    @abstractmethod
    def _on_stop(self):
        """ shutdown logic called when the service is stopped.
        Implementations should perform any additional shutdown tasks required by the
        service.
        """
    