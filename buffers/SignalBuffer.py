from dataclasses import dataclass
import threading
from PyDataGrabber.buffers.BufferException import BufferException
from PyDataGrabber.buffers.TimedBuffer import TimedBuffer
from PyDataGrabber.buffers.signals.Signal import Signal

@dataclass
class SignalBuffer(TimedBuffer):
    """
    A buffer that holds signals with a specific start time and elapsed time.
    
    Attributes:
        start_time (int): The start time of the signal in milliseconds.
        elapsed_time (float): The elapsed time since the start in seconds.
    """

    def __init__(self, signal : Signal = None, capacity: int = 1, sampling_period : int = 100):
        super().__init__()
        self.signal = signal
        self.capacity = capacity
        self.sampling_period = sampling_period
        self.signal_task() 
        
    def signal_task(self):
        """
        A task that samples the signal at regular intervals.
        This method should be overridden in subclasses to implement specific sampling logic.
        """
        if self.signal is not None:
            t, v = self.signal.value()
            self.push_timestamps(v, t)            
            threading.Timer(self.sampling_period / 1000.0, self.signal_task).start()            
        else:
            raise BufferException("No signal set for sampling.")
    
        
    

