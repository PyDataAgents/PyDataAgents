from typing import Tuple
import numpy as np
from .D2Geometry import D2Geometry


class BallscrewProfile(D2Geometry):
    
    def __init__(self, D_w : float = 1.0, f_r : float = 0.6, alpha : float = 45, s : float = 0.1, nut_or_spindle : bool = True):
        self.D_w = D_w
        self.f_r = f_r
        self.alpha = alpha
        self.s = s
        self.nut_or_spindle = nut_or_spindle
        self._r = self.D_w * self.f_r
        self._a_m_x = (self._r - self.D_w / 2) * np.cos(np.radians(self.alpha))
        self._a_m_y = (self._r - self.D_w /2) * np.sin(np.radians(self.alpha))
        
    def create(self, resolution : int = 100) -> Tuple[np.ndarray, np.ndarray]:                
        theta_1 = np.arcsin((self.s / 2 + self._a_m_y) / self._r)
        theta_2 = np.arccos(self._a_m_x / self._r)
        theta = np.linspace(theta_1, theta_2, resolution)
        return self.compute_profile(theta)
    
    def compute_profile(self, t) -> Tuple[np.ndarray, np.ndarray]:
        t = np.asarray(t)
        x_r = -self._a_m_x + self._r * np.cos(t)
        y_r = -self._a_m_y + self._r * np.sin(t)
        if self.nut_or_spindle is False:
            y_r = -y_r
        x_l = np.flip(-x_r)
        y_l = np.flip(y_r)
        x = np.append(x_r, x_l)
        y = np.append(y_r, y_l)
        return x, y
        