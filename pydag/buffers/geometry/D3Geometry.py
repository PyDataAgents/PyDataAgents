from abc import abstractmethod
from typing import Tuple
import numpy as np

from .D2Geometry import D2Geometry


class D3Geometry(D2Geometry):
        
    @abstractmethod
    def create(self, resolution_1 : int = 100, resolution_2 : int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        pass