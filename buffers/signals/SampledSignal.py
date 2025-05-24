from abc import ABC, abstractmethod
from typing import Tuple


class SampledSignal(ABC):
    """
    A class representing a sampled signal for continuously sampled data
    """

    def __init__(self, sample_rate : float):
        """
        Initializes the SampledSignal with sample rate
        """
        self.sample_rate = sample_rate
        self.sample_count : int = -1

    @abstractmethod
    def sample(self) -> Tuple[float, float]:
        self.sample_count += 1
        t = self.sample_count * 1.0 / self.sample_rate
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
    
    def reset(self):
        """
        Resets the signal's start time and sample count.
        """
        self.sample_count = -1