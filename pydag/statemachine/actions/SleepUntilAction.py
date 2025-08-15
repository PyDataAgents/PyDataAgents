from dataclasses import dataclass, field
import time

from ...utils.TimeUtils import TimeUtils
from ..Action import Action

@dataclass
class SleepUntilAction(Action):
    """
    An action that sleeps for a specified number of seconds.
    """
    
    daytime : str = field(init=True, default=None, metadata={"description" : "day time when the sleep should end"})

    def execute(self):
        seconds = TimeUtils.seconds_till_daytime(self.daytime)
        time.sleep(seconds)
        