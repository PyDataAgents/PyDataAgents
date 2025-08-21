from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Tuple
from ...statemachine.Node import Node

@dataclass
class SampledSignal(Node):
    """
    A class representing a sampled signal for continuously sampled data
    """
    sample_rate : float = field(default=1.0, metadata={"description": "sample rate of the signal in Hz"})
    sample_count : int = field(default=0, metadata={"description": "number of samples taken"})
        
    def __post_init__(self):
        super().__post_init__()

    @abstractmethod
    def sample(self) -> Tuple[float, float]:
        t = self.sample_count * 1.0 / self.sample_rate
        self.sample_count += 1
        return t, t
    
    def samples(self, n : int = 1) -> dict:
        for i in range(n):
            t, v = self.sample()
            if i == 0:
                times = [t]
                values = [v]
            else:
                times.append(t)
                values.append(v)
        return {"times": times, "values": values}
    
    def reset(self):
        """
        Resets the signal's start time and sample count.
        """
        self.sample_count = 0