import torch

class MLUtils:
    
    @staticmethod 
    def dict_to_tensor(data : dict) -> torch.tensor:
        return torch.tensor([v for v in data.values()])