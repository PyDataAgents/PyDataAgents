from dataclasses import dataclass, field
import time

from ...utils.TimeUtils import TimeUtils
from ..Action import Action

@dataclass
class SleepUntilAction(Action):
    """
    An action that sleeps until the specified daytime.
    """
    
    daytime : str = field(init=True, default=None, metadata={"description" : "day time when the sleep should end, format hh:mm:ss"})

    def _on_execute(self):
        seconds = TimeUtils.seconds_till_daytime(self.daytime)
        time.sleep(seconds)
        