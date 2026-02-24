from dataclasses import dataclass, field
from apscheduler.schedulers.background import BackgroundScheduler
from .BufferException import BufferException
from .TimedBuffer import TimedBuffer
from .signals.Signal import Signal
from ..agents.Agent import Agent

@dataclass
class SignalBuffer(TimedBuffer):
    """
    `Buffer` that holds signals with a specific start time and elapsed time and is defined by the referenced `signal`'s values.    
    """
    
    signal : Signal = field(default=None, metadata={"description": "a signal object to simulate data"})
    sampling_period : int = field(default=100, metadata={"description": "interval in milliseconds for update"})

    def __post_init__(self):
        super().__post_init__()
        self._scheduler : BackgroundScheduler = None        

    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._scheduler = BackgroundScheduler()
        self._scheduler.add_job(self.signal_task, 'interval', seconds=self.sampling_period / 1000.0)
        self._scheduler.start()
            
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        self._scheduler.shutdown()    
    
    def signal_task(self):
        """
        A task that samples the signal at regular intervals.
        This method should be overridden in subclasses to implement specific sampling logic.
        """
        if self.signal is not None:
            t, v = self.signal.value()  # Get the current time in milliseconds
            self.push_timestamps(v, t)
        else:
            raise BufferException("No signal set for sampling.")