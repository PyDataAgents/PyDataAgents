from dataclasses import dataclass, field

from ...utils.TimeUtils import TimeUtils
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
        self._count = 0
    
    def value(self, t : int = None) -> tuple[int, float]:
        ti, tf = super().value(t)
        if  self.times[self._count] <= tf:
            self._count += 1
            if self._count >= len(self.times):
                self._count = 0
                self.set(TimeUtils.utc_ms())
        return ti, self.values[self._count]