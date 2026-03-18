from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, field
import threading
from typing import TYPE_CHECKING


from ..agents.AgentStates import ServiceState
from ..agents.AgentElement import AgentElement, persisted_field, runtime_handle_field, transient_field


if TYPE_CHECKING:
    from ..agents.Agent import Agent

@dataclass
class Service(AgentElement):
    """abstract base class for agent Services
    """
    
    auto_start : bool = field(default=True, metadata={"description": "specifies whether to start the mapping with agent start"})
    _agent : "Agent" = transient_field(default=None, init=False, repr=False)
    _pause_event : threading.Event = runtime_handle_field(default_factory=threading.Event, init=False, repr=False)
    _quiesce_event : threading.Event = runtime_handle_field(default_factory=threading.Event, init=False, repr=False)
    _stop_event : threading.Event = runtime_handle_field(default_factory=threading.Event, init=False, repr=False)
    _heartbeat_ts : int = persisted_field(default=0, init=False, repr=False)
    _paused_state : bool = persisted_field(default=False, init=False, repr=False)
    _quiescing_state : bool = persisted_field(default=False, init=False, repr=False)
    _stopping_state : bool = persisted_field(default=False, init=False, repr=False)
        
    def __post_init__(self):
        super().__post_init__()
        self._sync_control_events()
    
    def _on_install(self, agent : "Agent" = None):
        self._agent = agent
        
    
    def _on_uninstall(self, agent : "Agent" = None):
        self._agent : None
    
    def start(self):
        """Start the service and mark it as running.

        Implementations should perform any startup tasks required by the service.
        """
        self._paused_state = False
        self._quiescing_state = False
        self._stopping_state = False
        self._sync_control_events()
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
        self._stopping_state = True
        self._sync_control_events()
        self._on_stop()
        self._state = ServiceState.STOPPED

    def pause(self):
        self._paused_state = True
        self._sync_control_events()

    def resume(self):
        self._paused_state = False
        self._quiescing_state = False
        self._stopping_state = False
        self._sync_control_events()
        if self._state == ServiceState.STOPPED:
            self.start()
        else:
            self._state = ServiceState.RUNNING

    def quiesce(self):
        self._quiescing_state = True
        self._paused_state = True
        self._sync_control_events()

    def is_paused(self) -> bool:
        return self._pause_event.is_set()

    def is_quiescing(self) -> bool:
        return self._quiesce_event.is_set()

    def is_stopping(self) -> bool:
        return self._stop_event.is_set()

    def heartbeat(self):
        from ..utils.TimeUtils import TimeUtils

        self._heartbeat_ts = TimeUtils.utc_ms()

    def restore_state(self, payload: dict | None):
        super().restore_state(payload)
        self._sync_control_events()

    def rebuild_runtime_handles(self, agent: "Agent" = None):
        self._sync_control_events()

    def _default_uid_prefix(self) -> str:
        return "service"
    
    
    @abstractmethod
    def _on_stop(self):
        """ shutdown logic called when the service is stopped.
        Implementations should perform any additional shutdown tasks required by the
        service.
        """

    def _sync_control_events(self):
        if self._paused_state:
            self._pause_event.set()
        else:
            self._pause_event.clear()
        if self._quiescing_state:
            self._quiesce_event.set()
        else:
            self._quiesce_event.clear()
        if self._stopping_state:
            self._stop_event.set()
        else:
            self._stop_event.clear()
    
