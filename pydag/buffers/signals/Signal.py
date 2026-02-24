from abc import abstractmethod
from typing import Tuple
from dataclasses import dataclass, field


from ...agents.Agent import Agent
from ...agents.AgentElement import AgentElement
from ...utils.TimeUtils import TimeUtils

@dataclass
class Signal(AgentElement):
    """
    Abstract base class for signals.
    """

    def __post_init__(self):
        super().__post_init__()
        self.start_time = TimeUtils.utc_ms()
        self.elapsed_time = 0.0
    
    def _on_install(self, agent : Agent = None):
        """
        Resets the signal's start time and elapsed time.
        """
        self.start_time = TimeUtils.utc_ms()
        self.elapsed_time = 0.0
    
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
                   
    def set(self, t : int):
        """
        Sets the start time of the signal to a specific timestamp.
        :param t: The timestamp in milliseconds.
        """
        self.start_time = t
        self.elapsed_time = 0.0
    
    @abstractmethod
    def value(self, t : int = None) -> Tuple[int, float]:
        """
        Returns the current value of the signal for the specified timestamp [ms]
        This method should be implemented by each subclasses.
        """
        if t is None:
            t = TimeUtils.utc_ms()
        self.elapsed_time = (t - self.start_time) / 1000.0
        return t, self.elapsed_time
    