from dataclasses import dataclass, field
from typing import Dict, Any
from ...transforms.Transform import Transform
import numpy as np

@dataclass
class ReshapeTransform(Transform):
    """ `Transform` that reshapes each sample to the specified shape. 
    Sample length is the length of the last dimension of the data, e.g. for time series data, it is the length of the time series.
    If sample_length is 0, no reshaping is applied. 
    If sample_length is greater than 0, each sample is reshaped to (..., -1, sample_length). That is, the last dimension is reshaped to have the specified sample_length, and the second to last dimension is adjusted accordingly.
    The other dimensions are kept the same. 
    If the total number of elements in the last dimension is not divisible by sample_length, the remainder is discarded.
    """
    
    sample_length : int = field(default=0, metadata={"description": "The length of each sample to which the data will be reshaped."})
            
    def transform(self, data : dict) -> Dict[str, list]:
        if self.sample_length <= 0:
            return data
        else:
            new_data = {}
            for key in data:
                # shorten last dimension to be multiple of sample_length
                len_last_dim = np.array(data[key]).shape[-1]
                floor_last_dim = len_last_dim // self.sample_length
                new_data[key] = np.array(data[key])[..., :floor_last_dim * self.sample_length]

                # reshape the last dimension and put multiples into the second to last dimension
                *prefix, m = np.array(new_data[key]).shape
                new_last_minus_1 = prefix[-1] * floor_last_dim if prefix else floor_last_dim
                new_shape = (*prefix[:-1], new_last_minus_1, self.sample_length) if prefix else (new_last_minus_1, self.sample_length)
                new_data[key] = np.array(new_data[key]).reshape(new_shape).tolist()

            return new_data