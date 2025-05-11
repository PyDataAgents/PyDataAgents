from PyDataGrabber.src.buffers.ListBuffer import ListBuffer

def test_000():
    buf1 = ListBuffer("B1", 100)
    buf1.push((1))
    print()
    print(buf1)
    print(buf1.config_options())

def test_010():
    buf1 = ListBuffer("B2", 3)
    buf1.push((1))
    buf1.push(2)
    buf1.push(3)
    print(buf1)
    buf1.push(4)
    print(buf1)
    print(buf1.config_options())

def test_020():
    buf1 = ListBuffer("B3", 5)
    buf1.push((1.0, 1.1, 1.2, 1.3))
    print(buf1)
    buf1.push((1.4, 1.5, 1.6))
    print(buf1)

def test_030():
    buf1 = ListBuffer("B4", 5)
    buf1.push((1.0, 1.1, 1.2, 1.3, 1.4))
    print(buf1)
    print(buf1.data(3, True))
    print(buf1)
    print(buf1.data(3, False))
    print(buf1)


