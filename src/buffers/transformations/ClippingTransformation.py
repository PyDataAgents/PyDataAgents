from dataclasses import dataclass, field
from PyDataGrabber.src.buffers.ObjectTransformation import ObjectTransformation


@dataclass
class ClippingTransformation(ObjectTransformation):
    
    lower_limit : float = field(default=0.0, metadata={"description": "lower limit for clipping"})
    upper_limit : float = field(default=1.0, metadata={"description": "upper limit for clipping"})
    
    def __init__(self):
        super().__init__()
        
    def apply(self, element: any) -> any:
        if element < self.lower_limit:
            return self.lower_limit
        elif element > self.upper_limit:
            return self.upper_limit
        else:
            return element