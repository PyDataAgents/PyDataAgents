from dataclasses import dataclass, field
import math
from .Signal import Signal

@dataclass
class Sawtooth(Signal):
    """
    A class to represent a sawtooth wave signal.
    """
    
    f : float = field(default=1.0, metadata={"description": "frequency of sawtooth wave in Hz"})
    a : float = field(default=1.0, metadata={"description": "amplitude of sawtooth wave"})
    

    def value(self, t: int = None) -> tuple[int, float]:
        """
        Returns the current value of the sawtooth wave signal for the specified timestamp [ms].

        :param t: The timestamp in milliseconds. If None, uses the current time.
        :return: A tuple containing the elapsed time in seconds and the sine value.
        """
        t, v = super().value()
        s = 2 * self.a * (v * self.f - math.floor(0.5 + v * self.f))
        return t, float(s)