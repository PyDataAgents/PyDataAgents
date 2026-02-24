from abc import abstractmethod
from dataclasses import dataclass
import time


from ..agents.AgentStates import NodeState
from .Action import Action


@dataclass
class TriggerAction(Action):
    """ Abstract `Action` `Node`that defines the interface for `Node`s with trigger logic, that are not executed directly within a `StatemachineService`,
    but are rather started from external events and trigger the execution `StatemachineService`.
    """
    
    def __post_init__(self):
        super().__post_init__()
        self._last_trigger : float = None
    
    @abstractmethod
    def start_trigger(self):
        """ starts the non-blocking trigger logic, that each TriggerAction sublass has to implement
        """
    
    def trigger(self):
        """ method that sets of the trigger action
        """
        self._state = NodeState.EXECUTING
        self._on_trigger()
        self._last_trigger = time.time()
        self._state = NodeState.IDLE
    
    @abstractmethod
    def _on_trigger(self):
        """ method / callback logic that is executed when the trigger detects an initiating event
        """
    
    def _on_execute(self):
        # do nothing, because the trigger logic executes the logic
        return