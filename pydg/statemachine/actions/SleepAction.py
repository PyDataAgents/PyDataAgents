from dataclasses import dataclass, field
import time

from ..Action import Action

@dataclass
class SleepAction(Action):
    """
    An action that sleeps for a specified number of seconds.
    """
    
    sleep_time : int = field(default=0, metadata={"description" : "number of seconds to sleep for"})

    def __init__(self):
        super().__init__()

    def execute(self):
        print(f"Sleeping for {self.sleep_time} seconds")
        time.sleep(self.sleep_time)
        print("Sleep action completed")