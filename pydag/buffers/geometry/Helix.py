from typing import Tuple

import numpy as np
from .D3Geometry import D3Geometry


class Helix(D3Geometry):
    
    def __init__(self, d : float = 1.0, P : float = 1.0, i : float = 1.0):
        self.d = d
        self.P = P
        self.i = i
    
    def create(self, resolution_1 : int = 100, resolution_2 : int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        t = np.linspace(0.0, self.i, resolution_1)
        return self.compute_helix(t)
    
    def compute_helix(self, t : np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        theta = 2 * np.pi * t
        x = self.d / 2 * np.cos(theta)
        y = self.d / 2 * np.sin(theta)
        z = self.P * t
        return x, y, z
        