from dataclasses import dataclass, field
import random
import pandas as pd

from pydag.services.datamodel.DataModel import DataModel
from pydag.services.datamodel.DataModelService import DataModelService

@dataclass
class SimpleLookupDataModel(DataModel):
    
    a : float = field(default=None, metadata={"description": "variable 1"})
    b : float = field(default=None, metadata={"description": "variable 2"})
    c : float = field(default=None, metadata={"description": "variable 3", "hidden": True})
    d : float = field(default=None, metadata={"description": "variable 4"})
    t : str = field(default=None, metadata={"description": "text variable 1", "hidden": True})
    
    
    def method1(self):
        self.b = self.a * 2 + 10.0
        self.c = random.randint(1, 10)
    
    def method2(self):
        self.t = f"Hello World {self.c}"
        
    def lookup1(self, dms : DataModelService):
        df : pd.DataFrame = dms.lookup_table("BUF")
        val = df.loc[df["A"] == self.a, "B"].tolist()
        self.d = val[0]