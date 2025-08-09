from pydag.buffers.DictBuffer import DictBuffer

def test_000():
    buf = DictBuffer()
    print(buf.config_options())
    
def test_010():
    buf = DictBuffer()
    buf.capacity = 5
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    print(buf.data())
    
def test_011():
    buf = DictBuffer()
    buf.capacity = 3
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    buf.push({"C1": 5, "C2": 6})
    print(buf.data())
    buf.push({"C1": 7, "C2": 8})
    print(buf.data())
    
def test_020():
    buf = DictBuffer()
    buf.capacity = 3
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    assert 2 == buf.size(), f"expected buffer size to be equal to 2 ({buf.size()})"
    
def test_030():
    buf = DictBuffer()
    buf.capacity = 5    
    d = [
        {"A": 1.0, "B": 2.0},
        {"A": 2.0, "B": 3.0},
        {"A": 3.0, "B": 4.0}
    ]    
    buf.push(d)    
    assert 3 == buf.size(), f"expected buffer size to be equal to 2 ({buf.size()})"
        
def test_40():
    buf = DictBuffer()
    buf.capacity = 10
    
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    
    d = {"C1": [5, 7], "C2": [6, 8]}
    
    buf.push(d)
    assert 4 == buf.size(), f"expected buffer size to be equal to 4 ({buf.size()})"
    