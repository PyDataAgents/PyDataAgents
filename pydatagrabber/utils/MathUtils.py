from math import pi, sin
import random


class MathUtils:
    
    @staticmethod
    def sine(t : float, a: float, f : float, p : float, n : float) -> float:
        """
            Computes the sine value based on the given parameters.
            Args:
                t (float): The time in seconds.
                a (float): The amplitude of the sine wave.
                f (float): The frequency of the sine wave in Hz.
                p (float): The phase of the sine wave in °.
                n (float): The noise ratio [0..1] relative to the amplitude a
        """
        x = a / 2 * sin(2 * pi * f * t + 2 * pi * p / 360.0) + n * a / 2 * (random.random() - 0.5)
        return x