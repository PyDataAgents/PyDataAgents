from PyDataGrabber.buffers.signals.SampledSignal import SampledSignal
from PyDataGrabber.utils.MathUtils import MathUtils


class SampledSine(SampledSignal):
    """
    A class to represent a sampled sine wave signal.
    
    Attributes:
        f (float): The frequency of the sine wave in Hz.
        a (float): The amplitude of the sine wave.
        sample_rate (int): The number of samples per second.
        p (float): The phase of the sine wave in °.
    """
    
    def __init__(self, sample_rate: float):
        super().__init__(sample_rate)
        self.a = 1.0
        self.f = 1.0
        self.n = 0.0
        self.p = 0.0
        
    def sample(self) -> tuple[float, float]:
        """
        Samples the sine wave signal at the current sample count.
        
        Returns:
            tuple: A tuple containing the timestamp and the sampled value.
        """
        t, v = super().sample()
        s = MathUtils.sine(t, self.a, self.f, self.p, self.n)        
        return t, s
    