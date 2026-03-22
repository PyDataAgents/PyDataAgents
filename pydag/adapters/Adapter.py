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
        
        Raises:
            AdapterException: if this `Adapter` could not be connected
        """
        # check valid state before connection
        self._check_state(AdapterState.CONNECTED)
        success = self._on_connect()
        if success:
            self._state = AdapterState.CONNECTED
        else:
            self._state = AgentElementState.ERROR
        return success
    
    @abstractmethod
    def _on_connect(self) -> bool:
        """
        connect logic specific to each `Adapter` implementation
        """
    
    def disconnect(self) -> bool:
        """
        disconnect from the data source/sink.    
        """
        self._check_state(AdapterState.DISCONNECTED)
        success = self._on_disconnect()
        if success:
            self._state = AdapterState.DISCONNECTED
        else:
            self._state = AgentElementState.ERROR
        return success

    @abstractmethod
    def _on_disconnect(self) -> bool:
        """
        disconnect logic specific to each `Adapter`implementation
        """
        
    def is_connected(self) -> bool:
        """ checks for `CONNECTED` state

        Returns:
            bool: True/False whether `Adapter` is connected
        """
        return self._state == AdapterState.CONNECTED
    
    def _check_state(self, next_state : AgentElementState):
        match(next_state):
            case AgentElementState.UNINSTALLED:
                if self._state != AdapterState.DISCONNECTED and self._state != AdapterState.CONNECTED and self._state != AgentElementState.INSTALLED and self._state != AgentElementState.ERROR:
                     raise AdapterException(f"{Adapter.__name__} {self.id} must be installed, connected, disconnected or have an error before uninstalling!")
                 
            case AgentElementState.INSTALLED:
                if self._state != AgentElementState.UNINSTALLED and self._state != AgentElementState.ERROR and self._state != AdapterState.CONNECTED and self._state != AdapterState.DISCONNECTED:
                    raise AdapterException(f"{Adapter.__name__} {self.id} must be uninstalled, connected, disconnected or have an error before installing!")
                
            case AdapterState.CONNECTED:
                if self._state != AgentElementState.INSTALLED and self._state != AdapterState.DISCONNECTED and self._state != AdapterState.PUBLISHING and self._state != AdapterState.SUBSCRIBING:
                    raise AdapterException(f"{Adapter.__name__} {self.id} must be installed, disconnected, subscribing or publishing before connecting!")
                
            case AdapterState.DISCONNECTED:
                if self._state != AdapterState.CONNECTED:
                    raise AdapterException(f"{Adapter.__name__} {self.id} must be connected before disconnecting!")
                
            case AdapterState.READING:
                if self._state != AdapterState.CONNECTED:
                    raise AdapterException(f"{Adapter.__name__} {self.id} must be connected before reading!")
                
            case AdapterState.WRITING:
                if self._state != AdapterState.CONNECTED:
                    raise AdapterException(f"{Adapter.__name__} {self.id} must be connected before writing!")
                
            case AdapterState.SUBSCRIBING:
                if self._state != AdapterState.CONNECTED:
                    raise AdapterException(f"{Adapter.__name__} {self.id} must be connected before subscribing!")
                
            case AdapterState.PUBLISHING:
                if self._state != AdapterState.CONNECTED:
                    raise AdapterException(f"{Adapter.__name__} {self.id} must be connected before publishing!")
                
            case AgentElementState.ERROR:
                # all other states are allowed
                return
        