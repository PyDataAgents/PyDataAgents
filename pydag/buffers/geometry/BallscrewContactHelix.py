import math
from typing import Tuple

import numpy as np

from .Helix import Helix


class BallscrewContactHelix(Helix):
    
    def __init__(self, D_pw : float = 1.0, D_w : float = 1.0, P : float = 1.0, i : float = 1.0, alpha : float = 45.0, nut_or_spindle : bool = True, left_or_right_flank : bool = True):
        self.alpha = alpha
        self.nut_or_spindle = nut_or_spindle
        self.left_or_right_flank = left_or_right_flank
        self.D_pw = D_pw
        self.D_w = D_w
        
        #nut
        if nut_or_spindle:            
            d = D_pw + self.D_w * math.cos(np.radians(self.alpha))            
        #spindle
        else:
            d = D_pw - self.D_w * math.cos(np.radians(self.alpha))
        
        super().__init__(d, P, i)
        
    def compute_helix(self, t) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        x, y, z = super().compute_helix(t)
        if self.left_or_right_flank:
            z = z - self.D_w / 2 *math.sin(np.radians(self.alpha))
        else:
            z = z + self.D_w / 2 *math.sin(np.radians(self.alpha))
        return x, y, z 
        

    