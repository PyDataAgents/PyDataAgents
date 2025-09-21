from dataclasses import dataclass, field
import time
from loguru import logger
from ..Action import Action

@dataclass
class SleepAction(Action):
    """
    An action that sleeps for a specified number of seconds.
    """
    
    sleep_time : int = field(init=True, default=0, metadata={"description" : "number of seconds to sleep for"})

    def execute(self):
        logger.debug(f"Sleeping for {self.sleep_time} seconds")
        time.sleep(self.sleep_time)
        logger.debug("Sleep action completed")