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
    assert 3 == buf.size(), f"expected buffer size to be equal to 3 ({buf.size()})"
        
def test_040():
    buf = DictBuffer()
    buf.capacity = 10
    
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    
    d = {"C1": [5, 7], "C2": [6, 8]}
    
    buf.push(d)
    assert 4 == buf.size(), f"expected buffer size to be equal to 4 ({buf.size()})"
    
    
def test_050():
    
    buf = DictBuffer(capacity=5)
    
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 2, "C2": 3})
    buf.push({"C1": 3, "C2": 4})
    
    print(buf.data())
    
    buf.push({"C1": 4, "C3": -1})
    
    print(buf.data())
    
def test_051():    
    buf = DictBuffer(capacity=5)    
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 2, "C2": 3})
    buf.push({"C1": 3, "C2": 4})    
    print(buf.data())    
    buf.push({"C1": [4, 5], "C3": [-1, -2]})    
    print(buf.data())


def test_052():    
    buf = DictBuffer(capacity=10, timestamps_enabled=True)    
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 2, "C2": 3})
    buf.push({"C1": 3, "C2": 4})      
    buf.push({"C1": [4, 5], "C3": [-1, -2]})    
    buf.push({"C3": [6,7,8], "C4": [8,9,10]})
    assert all(len(v) == buf.size() for v in buf.data().values()), "Buffer columns have different lengths"

def test_053():  
    #test with limited capacity  
    buf = DictBuffer(capacity=5, timestamps_enabled=True)    
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 2, "C2": 3})
    buf.push({"C1": 3, "C2": 4})    
    buf.push({"C1": [4, 5], "C3": [-1, -2]})    
    buf.push({"C3": [6,7,8], "C4": [8,9,10]})
    assert all(len(v) == 5 for v in buf.data().values()), "Buffer columns have different lengths"


if __name__ == "__main__":
    #test_000()
    #test_010()
    #test_011()
    #test_020()
    #test_030()
    #test_040()
    #test_050()
    #test_051()
    #test_052()
    test_053()
       