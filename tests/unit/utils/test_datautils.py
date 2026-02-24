import numpy as np
from pydag.utils.DataUtils import DataUtils


class TestClass1:    
    def __init__(self):
        self.a = 10
        self.b = 'a'
        self.c = TestClass2()
        
class TestClass2:    
    def __init__(self):
        self.d = 'Joe'
        self.e = 10.1

def test_000():
    
    tc = TestClass1()
    print(DataUtils.obj_to_dict(tc))
    
def test_001():    
    d = {"a": [1,2,3]}    
    a = DataUtils.dict_to_ndarray(d)    
    print(a)
    
def test_002():    
    d = {"a": [1,2,3], "v": [4,5,6]}    
    a = DataUtils.dict_to_ndarray(d)    
    print(a)
    
def test_010():
    a = np.array([1,2,3])
    d = DataUtils.ndarray_to_dict(a)
    print(d)
    
def test_011():
    a = np.array([[1,2,3], [3,4,5]])
    d = DataUtils.ndarray_to_dict(a)
    print(d)
    