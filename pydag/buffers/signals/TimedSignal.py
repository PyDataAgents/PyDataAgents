from dataclasses import dataclass, field

from ...buffers.signals.Signal import Signal


@dataclass
class TimedSignal(Signal):
    """
    A signal that emits values at specified time intervals.
    """
    
    times : list[float] = field(default_factory=list, metadata={"description": "list of times in seconds when the signal should emit a value"})
    values : list[float] = field(default_factory=list, metadata={"description": "list of values to emit at the specified times"})
    
    def __post_init__(self):
        super().__post_init__()
        self.count = 0
    
    def value(self, t : int = None) -> tuple[int, float]:
        ti, tf = super().value(t)
        if  self.times[self.count] <= tf:
            self.count += 1
            if self.count >= len(self.times):
                self.count = 0
                self.install()
        return ti, self.values[self.count]