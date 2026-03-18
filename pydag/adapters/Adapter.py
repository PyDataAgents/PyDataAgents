from __future__ import annotations
from abc import abstractmethod
from typing import Union


from .AdapterException import AdapterException
from ..agents.AgentStates import AdapterState, AgentElementState
from ..agents.AgentElement import AgentElement


class Adapter(AgentElement):
    """
    Abstract base class for `Adapters`. All `Adapters` must inherit from this class.
    """
    
    def __post_init__(self):
        super().__post_init__()
        self._state : Union[AdapterState, AgentElementState] = AgentElementState.UNINSTALLED
    
    def connect(self) -> bool:
        """
        connect to the data source/sink.
        """
        # check valid state before connection
        if self._state == AdapterState.DISCONNECTED or self._state == AgentElementState.INSTALLED:
            success = self._on_connect()
            if success:
                self._state = AdapterState.CONNECTED
            else:
                self._state = AgentElementState.ERROR
            return success
        else:
            raise AdapterException(f"{Adapter.__name__} '{self.id}' must be in state {AdapterState.DISCONNECTED} or {AgentElementState.INSTALLED} in order to connect")
    
    @abstractmethod
    def _on_connect(self) -> bool:
        """
        connect logic specific to each `Adapter` implementation
        """
    
    def disconnect(self) -> bool:
        """
        disconnect from the data source/sink.    
        """
        if self._state == AdapterState.CONNECTED:
            success = self._on_disconnect()
            if success:
                self._state = AdapterState.DISCONNECTED
            else:
                self._state = AgentElementState.ERROR
            return success
        else:
            raise AdapterException(f"{Adapter.__name__} '{self.id}' must be in state {AdapterState.CONNECTED} in order to disconnect")

    @abstractmethod
    def _on_disconnect(self) -> bool:
        """
        disconnect logic specific to each `Adapter`implementation
        """
        