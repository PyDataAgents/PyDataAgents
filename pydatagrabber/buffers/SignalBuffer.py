from dataclasses import dataclass, field
from time import time
from apscheduler.schedulers.background import BackgroundScheduler
from .BufferException import BufferException
from .TimedBuffer import TimedBuffer
from .signals.Signal import Signal
from ..grabbers.Grabber import Grabber

@dataclass
class SignalBuffer(TimedBuffer):
    """
    A buffer that holds signals with a specific start time and elapsed time.
    
    Attributes:
        start_time (int): The start time of the signal in milliseconds.
        elapsed_time (float): The elapsed time since the start in seconds.
    """
    
    signal : Signal = field(default=None, metadata={"description": "a signal object to simulate data"})
    sampling_period : int = field(default=100, metadata={"description": "interval in milliseconds for update"})

    def __init__(self):
        super().__init__()
        self.scheduler : BackgroundScheduler = None        

    def install(self, grabber : Grabber = None):
        super().install(grabber)
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.signal_task, 'interval', seconds=self.sampling_period / 1000.0)
        self.scheduler.start()
            
    def deinstall(self, grabber : Grabber = None):
        super().deinstall(grabber)
        self.scheduler.shutdown()    
    
    def signal_task(self):
        """
        A task that samples the signal at regular intervals.
        This method should be overridden in subclasses to implement specific sampling logic.
        """
        if self.signal is not None:
            t, v = self.signal.value()  # Get the current time in milliseconds
            self.push_timestamps([v], [t])
        else:
            raise BufferException("No signal set for sampling.")