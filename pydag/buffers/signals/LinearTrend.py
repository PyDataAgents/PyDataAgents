from dataclasses import dataclass, field
from typing import Tuple

from ...utils.MathUtils import MathUtils
from ...buffers.signals.Signal import Signal


@dataclass
class LinearTrend(Signal):
    """
    A signal that simulates a linear trend
    """
    
    min : float = field(default=0.0, metadata={"description": "minimum value of the trend"})
    max : float = field(default=100.0, metadata={"description": "maximum value of the trend"})
    duration : int = field(default=1000 * 1000, metadata={"description": "duration of the trend in milliseconds"})
    noise : float = field(default=0.0, metadata={"description": "noise to add to the trend [0..1]"})
        
    def value(self, t : int = None) -> Tuple[int, float]:
        ti, tf = super().value(t)
        if tf > self.duration:
            self.install()
        return ti, self._trend(tf)
    
    def _trend(self, tf : float) -> float:
        """
        Calculates the linear trend value at time tf
        """        
        v = self.min + (self.max - self.min) * (tf / self.duration) + (self.min + self.max) / 2 * self.noise * (2 * MathUtils.rand() - 1)
        return tf, v