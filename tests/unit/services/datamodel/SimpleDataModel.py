from dataclasses import dataclass, field
import os
from pydag.services.datamodel.DataModel import DataModel

@dataclass
class SimpleDataModel(DataModel):
    """ A simple data model for testing purposes. """
    
    a : float = field(default=None, metadata={"description": "variable 1 - test description", "unit": "m", "ui_label": "Variable a"})
    b : float = field(default=None, metadata={"description": "variable 2", "unit": "kg"})
    c : float = field(default=None, metadata={"description": "variable 3", "hidden": False})
    t : str = field(default=None, metadata={"description": "text variable 1", "hidden": True})
    i : str = field(default=f"{os.path.dirname(__file__)}/placeholder.png", metadata={"description": "an example image", "ui_type": "image"})
    m : str = field(default=None, metadata={"description": "variable m", "hidden": False})
    
    def method1(self):
        self.b = self.a * 2 + 10.0
        self.c = self.a + self.b
    
    def method2(self):
        self.t = f"Hello World {self.c}"
                
    def method3(self):
        if self.a % 2 == 0:
            self.i = f"{os.path.dirname(__file__)}/placeholder.png"
        else:
            self.i = f"{os.path.dirname(__file__)}/placeholder2.png"
            
    def method4(self):
        self.m = f"Hello World {self.a}!"