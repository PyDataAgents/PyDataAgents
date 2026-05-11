import random

from pydag.buffers.signals.Signal import Signal


class RandBoolean(Signal):
    
    def value(self, t: int = None) -> tuple[int, float]:
        """
        Returns a random boolean value.

        :param t: The timestamp in milliseconds. If None, uses the current time.
        :return: A tuple containing the timestamp in ms and the boolean value.
        """
        t, et = super().value()
        s = random.getrandbits(1) == 1
        return t, s