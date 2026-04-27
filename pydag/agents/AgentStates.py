from collections import deque
from enum import Enum

from ..utils.TimeUtils import TimeUtils


class AgentElementState():
    INSTALLED = "INSTALLED"
    UNINSTALLED = "UNINSTALLED"
    ERROR = "ERROR"
 
class BufferState(AgentElementState):
    RETRIEVING = "RETRIEVING"
    STORING = "STORING"
        
class NodeState(AgentElementState):
    EXECUTING = "EXECUTING"
    
class ServiceState(AgentElementState):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    
class LearningState(NodeState):
    LEARNING = "LEARNING"
    INFERING = "INFERING"
    PREPROCESSING = "PREPROCESSING"
    
   
MAX_HISTORY = 5 

class StateHistory():    
    
    def __post_init__(self):
        self._states : deque = deque(maxlen=MAX_HISTORY)
        self._timestamps : deque = deque(maxlen=MAX_HISTORY)
        
    def set_state(self, state : Enum):
        self._states.append(state)
        self._timestamps.append(TimeUtils.utc_ms())
        
    def get_state(self) -> Enum:
        if len(self._states) > 0:
            return self._states[-1]
        else:
            return None
        
    def get_history(self) -> tuple[list[Enum], list[float]]:
        return list(self._states), list(self._timestamps)