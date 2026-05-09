from dataclasses import dataclass, field
from .Signal import Signal
from ...utils.MathUtils import MathUtils

@dataclass
class Sine(Signal):
    """
    A class to represent a sine wave signal.
    """
    
    f : float = field(default=1.0, metadata={"description": "frequency of sine wave in Hz"})
    a : float = field(default=1.0, metadata={"description": "amplitude of sine wave"})
    p : float = field(default=0.0, metadata={"description": "phase angle of sine wave in °"})
    n : float = field(default=0.0, metadata={"description": "noise level of sine wave in respect to ampltidue [0..1]"})

    def value(self, t: int = None) -> tuple[int, float]:
        """
        Returns the current value of the sine wave signal for the specified timestamp [ms].

        :param t: The timestamp in milliseconds. If None, uses the current time.
        :return: A tuple containing the elapsed time in seconds and the sine value.
        """
        t, et = super().value()
        s = MathUtils.sine(et, self.a, self.f, self.p, self.n)
        return t, s