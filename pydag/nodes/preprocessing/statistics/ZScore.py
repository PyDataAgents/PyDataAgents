from dataclasses import dataclass
import numpy as np
from loguru import logger


from ...BufferNode import BufferNode


@dataclass
class ZScore(BufferNode):
        
    def _on_execute(self, data : dict):
        new_data = self.get_parent_data()
        for key in data:
            ar = np.array(data[key])
            std = ar.std()
            if std == 0:
                logger.debug(f"Warning: Standard deviation is zero during Z-Score normalization for key '{key}'. Original Data will be used.")
                zscores = ar
            else:
                zscores : np.ndarray = (ar - ar.mean()) / (ar.std())
            new_data[key] = zscores.tolist()
            
        self._buffer.push(new_data)