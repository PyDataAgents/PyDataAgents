from dataclasses import dataclass, field
from pydag.services.datamodel.DataModel import DataModel

@dataclass
class SimpleDataModel(DataModel):
    """ A simple data model for testing purposes. """
    
    a : float = field(default=None, metadata={"description": "variable 1 - test description", "unit": "m"})
    b : float = field(default=None, metadata={"description": "variable 2", "unit": "kg"})
    c : float = field(default=None, metadata={"description": "variable 3", "hidden": False})
    t : str = field(default=None, metadata={"description": "text variable 1", "hidden": True})
    
    def method1(self):
        self.b = self.a * 2 + 10.0
        self.c = self.a + self.b
    
    def method2(self):
        self.t = f"Hello World {self.c}"