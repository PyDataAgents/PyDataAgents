from pydag.buffers.DataType import DataType
from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.http.HttpGetAction import HttpGetAction
from pydag.nodes.http.HttpPostAction import HttpPostAction


def test_000():
    
    hga = HttpGetAction(url = "https://httpbin.org/get")
    hga.install()
    
    hga.execute()
    
    print(hga.buffer.data())
    
    
def test_010():
    
    hga = HttpGetAction(url = "https://httpbin.org/get", json_path="$.headers")
    hga.install()
    
    hga.execute()
    
    print(hga.buffer.data())
    
    
def test_020():
    
    buf = ListBuffer(capacity=1, data_type = DataType.STRING.value)
    buf.push("{'key1': 'value', 'key2': [1.0, 2.0, 3.0]}")
    
    hpa = HttpPostAction(url = "https://httpbin.org/post")
    hpa.buffer = buf
    hpa.install()
    hpa.execute()