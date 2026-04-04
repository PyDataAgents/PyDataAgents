from dataclasses import dataclass, field
from pydag.services.datamodel.DataModel import DataModel

@dataclass
class AnotherSimpleDataModel(DataModel):
    
    x : float = field(default=None, metadata={"description": "variable 1"})
    y : float = field(default=None, metadata={"description": "variable 2"})
    z : float = field(default=None, metadata={"description": "variable 3"})
    
    def yy(self):
        self.y = 3 * self.x - 10.0
           
    def zz(self):
        self.z = self.x + self.y