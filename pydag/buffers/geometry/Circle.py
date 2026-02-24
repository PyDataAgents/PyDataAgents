from typing import Tuple
import numpy as np
from .D2Geometry import D2Geometry


class Circle(D2Geometry):
    
    def __init__(self, r : float = 1.0, x_c : float = 0.0, y_c : float = 0.0):
        self.r = r
        self.x_c = x_c
        self.y_c = y_c
    
    def create(self, resolution : int = 100) -> Tuple[np.ndarray, np.ndarray]:
        theta = np.linspace(0.0, 2 * np.pi, resolution)
        x = self.r * np.cos(theta)
        y = self.r * np.sin(theta)
        return x, y