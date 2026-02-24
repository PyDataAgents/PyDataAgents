from abc import abstractmethod
from dataclasses import dataclass
from typing import Tuple
import numpy as np

@dataclass
class D2Geometry():
        
    @abstractmethod
    def create(self, resolution : int = 100) -> Tuple[np.ndarray, np.ndarray]:
        pass