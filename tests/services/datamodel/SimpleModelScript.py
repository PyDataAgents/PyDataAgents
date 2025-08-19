"""
Script file containing all calculation rules.
The input arguments for each method are always dataclass objects and lookup table stores/collections.
"""

from pydag.services.datamodel.DataModel import DataModel


def method1(dm : DataModel):
    dm.b = dm.a * 2 + 10.0
    dm.c = dm.a + dm.b
    
def method2(dm : DataModel):
    dm.t = f"Hello World {dm.c}"