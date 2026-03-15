from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, field
import threading
from typing import Any
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
        self._pause_event = threading.Event()
        self._quiesce_event = threading.Event()
        self._stop_event = threading.Event()
        self._heartbeat_ts : int = 0
    
    def _on_install(self, agent : "Agent" = None):
        self._agent = agent
        
    
    def _on_uninstall(self, agent : "Agent" = None):
        self._agent : None
    
    def start(self):
        """Start the service and mark it as running.

        Implementations should perform any startup tasks required by the service.
        """
        self._pause_event.clear()
        self._quiesce_event.clear()
        self._stop_event.clear()
        self._state = ServiceState.RUNNING
        self._on_start()
        self.heartbeat()
    
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
        self._stop_event.set()
        self._on_stop()
        self._state = ServiceState.STOPPED

    def pause(self):
        self._pause_event.set()

    def resume(self):
        self._pause_event.clear()
        if self._state == ServiceState.STOPPED:
            self.start()
        else:
            self._state = ServiceState.RUNNING

    def quiesce(self):
        self._quiesce_event.set()
        self.pause()

    def is_paused(self) -> bool:
        return self._pause_event.is_set()

    def is_quiescing(self) -> bool:
        return self._quiesce_event.is_set()

    def is_stopping(self) -> bool:
        return self._stop_event.is_set()

    def heartbeat(self):
        from ..utils.TimeUtils import TimeUtils

        self._heartbeat_ts = TimeUtils.utc_ms()

    def snapshot_state(self) -> dict[str, Any]:
        payload = super().snapshot_state()
        payload.update(
            {
                "heartbeat_ts": self._heartbeat_ts,
                "paused": self.is_paused(),
                "quiescing": self.is_quiescing(),
                "stopping": self.is_stopping(),
            }
        )
        return payload

    def restore_state(self, payload: dict | None):
        super().restore_state(payload)
        if payload is None:
            return
        self._heartbeat_ts = payload.get("heartbeat_ts", 0)
        if payload.get("paused"):
            self._pause_event.set()
        else:
            self._pause_event.clear()
        if payload.get("quiescing"):
            self._quiesce_event.set()
        else:
            self._quiesce_event.clear()
        if payload.get("stopping"):
            self._stop_event.set()
        else:
            self._stop_event.clear()
    
    
    @abstractmethod
    def _on_stop(self):
        """ shutdown logic called when the service is stopped.
        Implementations should perform any additional shutdown tasks required by the
        service.
        """
    
