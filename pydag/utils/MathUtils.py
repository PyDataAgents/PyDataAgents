from math import pi, sin
import random
from typing import Tuple

import numpy as np


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
    
    @staticmethod
    def rand() -> float:
        """
        Returns a random float value between 0 and 1.
        """
        return random.random()
    
    @staticmethod
    def circle(radius : float = 1.0, x_0 : float = 0.0, y_0 : float = 0.0, n : int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate x and y coordinates for a circle.

        Parameters
        ----------
        radius : float, optional
            The radius of the circle (default is 1.0).
        x_0 : x coordinate of the circle's center
        y_0 : y coordinate of the circle's center
        n : int, optional
            The number of points to generate around the circle (default is 100).

        Returns
        -------
        x : np.ndarray
            The x coordinates of points on the circle.
        y : np.ndarray
            The y coordinates of points on the circle.
        
        Example
        -------
        >>> x, y = generate_circle(radius=5, x_0=0, y_0=0, n=50)
        >>> plt.plot(x, y)
        >>> plt.axis("equal")
        >>> plt.show()
        """
        # Generate angles
        theta = np.linspace(0, 2 * np.pi, n)
        # Compute x and y coordinates
        x = x_0 + radius * np.cos(theta)
        y = y_0 + radius * np.sin(theta)
        return x, y
        