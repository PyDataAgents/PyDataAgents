from typing import Any

import numpy as np
import torch

class MLUtils:
    
    @staticmethod 
    def dict_to_tensor(data : dict) -> torch.tensor:
        return torch.tensor([v for v in data.values()])
    
    @staticmethod
    def reshape(data : dict[str, Any], sample_length : int):
        if sample_length <= 0:
            return data
        else:
            new_data = {}
            for key in data:
                # shorten last dimension to be multiple of sample_length
                len_last_dim = np.array(data[key]).shape[-1]
                floor_last_dim = len_last_dim // sample_length
                new_data[key] = np.array(data[key])[..., :floor_last_dim * sample_length]

                # reshape the last dimension and put multiples into the second to last dimension
                *prefix, m = np.array(new_data[key]).shape
                new_last_minus_1 = prefix[-1] * floor_last_dim if prefix else floor_last_dim
                new_shape = (*prefix[:-1], new_last_minus_1, sample_length) if prefix else (new_last_minus_1, sample_length)
                new_data[key] = np.array(new_data[key]).reshape(new_shape).tolist()

            return new_data