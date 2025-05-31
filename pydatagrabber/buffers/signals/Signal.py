from abc import abstractmethod
from typing import Tuple

from PyDataGrabber.pydatagrabber.grabbers.GrabberElement import GrabberElement
from PyDataGrabber.pydatagrabber.utils.TimeUtils import TimeUtils

class Signal(GrabberElement):
    """
    Abstract base class for signals.
    """

    def __init__(self):
        self.start_time = TimeUtils.utc_ms()
        self.elapsed_time = 0.0
    
    def reset(self):
        """
        Resets the signal's start time and elapsed time.
        """
        self.start_time = TimeUtils.utc_ms()
        self.elapsed_time = 0.0
        
    def set(self, t : int):
        """
        Sets the start time of the signal to a specific timestamp.
        :param t: The timestamp in milliseconds.
        """
        self.start_time = t
        self.elapsed_time = 0.0
    
    @abstractmethod
    def value(self, t : int = None) -> Tuple[int, float]:
        """
        Returns the current value of the signal for the specified timestamp [ms]
        This method should be implemented by each subclasses.
        """
        if t is None:
            t = TimeUtils.utc_ms()
        self.elapsed_time = (t - self.start_time) / 1000.0
        return t, self.elapsed_time
    