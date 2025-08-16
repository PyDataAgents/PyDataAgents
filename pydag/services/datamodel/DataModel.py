from abc import ABC
from dataclasses import dataclass
from typing import Any
import loguru


@dataclass
class DataModel(ABC):
    
    def set_data(self, property_name : str, value : Any):
        if hasattr(self, property_name):
            setattr(self, property_name, value)
        else
                  
        
            
    def to_dict(self):
        pass