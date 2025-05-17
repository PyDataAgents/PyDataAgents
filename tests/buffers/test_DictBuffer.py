from PyDataGrabber.src.buffers.DictBuffer import DictBuffer

def test000():
    buf = DictBuffer("B1")
    print(buf.config_options())
    
def test010():
    buf = DictBuffer("B1", 3)
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    print(buf.data())
    
def test011():
    buf = DictBuffer("B1", 3)
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    buf.push({"C1": 5, "C2": 6})
    print(buf.data())
    buf.push({"C1": 7, "C2": 8})
    print(buf.data())