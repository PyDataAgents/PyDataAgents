from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Tuple


from ...agents.Agent import Agent
from ...agents.AgentElement import AgentElement

@dataclass
class SampledSignal(AgentElement):
    """
    A class representing a sampled signal for continuously sampled data
    """
    sample_rate : float = field(default=1.0, metadata={"description": "sample rate of the signal in Hz"})
            
    def __post_init__(self):
        super().__post_init__()
        self.sample_count : int = 0

    def _on_install(self, agent : Agent = None):        
        """
        Resets the signal's start time and sample count.
        """
        self.sample_count = 0
    
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)

    @abstractmethod
    def sample(self) -> Tuple[float, float]:
        t = self.sample_count * 1.0 / self.sample_rate
        self.sample_count += 1
        return t, t
    
    def samples(self, n : int = 1) -> Tuple[list[float], list[float]]:
        for i in range(n):
            t, v = self.sample()
            if i == 0:
                times = [t]
                values = [v]
            else:
                times.append(t)
                values.append(v)
        return times, values    