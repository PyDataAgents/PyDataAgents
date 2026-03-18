from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from ..agents.AgentStates import AdapterState, AgentElementState
from ..agents.AgentElement import AgentElement, persisted_field

@dataclass
class Adapter(AgentElement):
    """
    Abstract base class for `Adapters`. All `Adapters` must inherit from this class.
    """

    _side_effect_receipts : list[dict[str, Any]] = persisted_field(default_factory=list, init=False, repr=False)
    
    def connect(self) -> bool:
        """
        connect to the data source/sink.
        """
        success = self._on_connect()
        if success:
            self._state = AdapterState.CONNECTED
        else:
            self._state = AdapterState.DISCONNECTED
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

    def record_side_effect_receipt(self, receipt: dict[str, Any]):
        self._side_effect_receipts.append(receipt)

    def _default_uid_prefix(self) -> str:
        return "adapter"
        
