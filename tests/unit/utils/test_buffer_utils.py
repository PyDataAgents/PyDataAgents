import os
from pydag.buffers.DictBuffer import DictBuffer
from pydag.utils.DataUtils import DataUtils
from pydag.utils.HTMLUtils import HTMLUtils

def test_000():
    buf = DictBuffer(capacity = 3)
    buf.install()
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    buf.push({"C1": 5, "C2": 6})
    html = HTMLUtils.dict_to_htmltable(buf.data())
    print(html)
    
def test_010():
    buf = DictBuffer(capacity = 3)
    buf.install()
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    buf.push({"C1": 5, "C2": 6})
    html = HTMLUtils.dict_to_htmltable(buf.data())
    path = os.path.dirname(__file__) + os.sep + "test_table.html"
    with open(path, "w", encoding="utf-8") as f:
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
    buf = DictBuffer(capacity = 3)
    buf.install()
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    buf.push({"C1": 5, "C2": 6})
    
    d = buf.data()
    print(d)
    
    buf.push({"C1": 7, "C2": 8})
    print(d)
