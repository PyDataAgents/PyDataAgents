from PyDataGrabber.src.buffers.signals.Signal import Signal
from PyDataGrabber.src.utils.MathUtils import MathUtils


class Sine(Signal):
    """
    A class to represent a sine wave signal.
    """

    def __init__(self):
        """
        Initializes the Sine signal with frequency, amplitude, and phase.

        :param frequency: Frequency of the sine wave in Hz.
        :param amplitude: Amplitude of the sine wave.
        :param phase: Phase shift of the sine wave in radians.
        """
        super().__init__()
        self.f = 1.0
        self.a = 1.0
        self.p = 0.0
        self.n = 0.0
        
    def value(self, t: int = None) -> tuple[int, float]:
        """
        Returns the current value of the sine wave signal for the specified timestamp [ms].

        :param t: The timestamp in milliseconds. If None, uses the current time.
        :return: A tuple containing the elapsed time in seconds and the sine value.
        """
        t, v = super().value()
        s = MathUtils.sine(t, self.a, self.f, self.p, self.n)
        return t, s