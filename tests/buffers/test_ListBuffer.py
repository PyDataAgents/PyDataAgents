from PyDataGrabber.src.buffers.ListBuffer import ListBuffer

def test_000():
    buf1 = ListBuffer("B1", 100)
    buf1.push((1))
    print(buf1)


test_000()
        

