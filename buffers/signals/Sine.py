from dataclasses import dataclass, field
from PyDataGrabber.buffers.signals.Signal import Signal
from PyDataGrabber.utils.MathUtils import MathUtils

@dataclass
class Sine(Signal):
    """
    A class to represent a sine wave signal.
    """
    
    f : float = field(default=1.0, metadata={"description": "frequency of sine wave in Hz"})
    a : float = field(default=1.0, metadata={"description": "amplitude of sine wave"})
    p : float = field(default=0.0, metadata={"description": "phase angle of sine wave in °"})
    n : float = field(default=0.0, metadata={"description": "noise level of sine wave in respect to ampltidue [0..1]"})

    def __init__(self):
        """
        Initializes the Sine signal with frequency, amplitude, and phase.

        :param frequency: Frequency of the sine wave in Hz.
        :param amplitude: Amplitude of the sine wave.
        :param phase: Phase shift of the sine wave in radians.
        """
        super().__init__()
        
    def value(self, t: int = None) -> tuple[int, float]:
        """
        Returns the current value of the sine wave signal for the specified timestamp [ms].

        :param t: The timestamp in milliseconds. If None, uses the current time.
        :return: A tuple containing the elapsed time in seconds and the sine value.
        """
        t, v = super().value()
        s = MathUtils.sine(t, self.a, self.f, self.p, self.n)
        return t, s