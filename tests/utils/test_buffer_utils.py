import os
from pydag.buffers.DictBuffer import DictBuffer
from pydag.utils.DataUtils import DataUtils

def test_000():
    buf = DictBuffer()
    buf.capacity = 3
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    buf.push({"C1": 5, "C2": 6})
    html = buf.to_html()
    print(html)
    
def test_010():
    buf = DictBuffer()
    buf.capacity = 3
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    buf.push({"C1": 5, "C2": 6})
    html = buf.to_html()
    path = os.getcwd() + "\\tests\\data\\table_html.html"
    with open(path, "w") as f:
        f.write(html)
        
def test_020():
    d = [{"A": 1, "B": 2}, {"A": 3, "B": 4}]
    dd = DataUtils.list_to_dict(d)
    print(dd)  
    
def test_030():
    d = {"A": [1, 3], "B": [2, 4]}     
    dd = DataUtils.dict_to_list(d)
    print(dd)
    
def test_040():
    buf = DictBuffer()
    buf.capacity = 3
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    buf.push({"C1": 5, "C2": 6})
    
    d = buf.data()
    print(d)
    
    buf.push({"C1": 7, "C2": 8})
    print(d)

    