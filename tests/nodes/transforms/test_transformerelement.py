import numpy as np
from pydag.utils.DataUtils import DataUtils


def test_000():    
    d = {"a": [1,2,3]}    
    a = DataUtils.dict_to_ndarray(d)    
    print(a)
    
def test_001():    
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