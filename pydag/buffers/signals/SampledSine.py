from dataclasses import dataclass, field
from ...buffers.signals.SampledSignal import SampledSignal
from ...utils.MathUtils import MathUtils

@dataclass
class SampledSine(SampledSignal):
    """
    A class to represent a sampled sine wave signal.
    
    Attributes:
        f (float): The frequency of the sine wave in Hz.
        a (float): The amplitude of the sine wave.
        sample_rate (int): The number of samples per second.
        p (float): The phase of the sine wave in °.
    """
    
    f : float = field(default=1.0, metadata={"description": "frequency of sine wave in Hz"})
    a : float = field(default=1.0, metadata={"description": "amplitude of sine wave"})
    p : float = field(default=0.0, metadata={"description": "phase angle of sine wave in °"})
    n : float = field(default=0.0, metadata={"description": "noise level of sine wave in respect to ampltidue [0..1]"})
    

    def __post_init__(self):
        super().__post_init__()
        
    def sample(self) -> tuple[float, float]:
        """
        Samples the sine wave signal at the current sample count.
        
        Returns:
            tuple: A tuple containing the timestamp and the sampled value.
        """
        t, v = super().sample()
        s = MathUtils.sine(t, self.a, self.f, self.p, self.n)        
        return t, s
    