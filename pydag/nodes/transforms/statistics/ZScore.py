import numpy as np

from ..Transform import Transform

class ZScore(Transform):
    
    #def __init__(self):
    #    super().__init__()
    
    def transform(self, data : dict):
        new_data = {}
        for key in data:
            ar = np.array(data[key])
            std = ar.std()
            if std == 0:
                print("Warning: Standard deviation is zero during Z-Score normalization. Original Data will be used.")
                zscores = ar
            else:
                zscores : np.ndarray = (ar - ar.mean()) / (ar.std())
            new_data[key] = zscores.tolist()
        return new_data