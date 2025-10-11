from dataclasses import dataclass, field
from ...transforms.Transform import Transform

@dataclass
class SplitKeyTransform(Transform):
    """ `Transform` that extracts the specified keys from data dictionary
    """
    
    split_keys : list[str] = field(init=True, default_factory=list[str], metadata={"description": "keys to extract from data dict"})
            
    def transform(self, data : dict):
        new_data = {}
        for key in self.split_keys:
            if key in data:
                new_data[key] = data[key]
        return new_data