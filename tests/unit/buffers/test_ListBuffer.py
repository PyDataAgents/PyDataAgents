from pydag.buffers.ListBuffer import ListBuffer
from pydag.agents.AgentKeywords import AgentKeywords
import numpy as np

def test_000():
    buf1 = ListBuffer()
    buf1.install()
    buf1.push((1))
    print()
    print(buf1)
    print(buf1.config_options())

def test_010():
    buf1 = ListBuffer()
    buf1.capacity = 5
    buf1.install()
    buf1.push((1))
    buf1.push(2)
    buf1.push(3)
    print(buf1)
    buf1.push(4)
    print(buf1)
    print(buf1.config_options())

def test_020():
    buf1 = ListBuffer()
    buf1.capacity = 5
    buf1.install()
    buf1.push((1.0, 1.1, 1.2, 1.3))
    print(buf1)
    buf1.push((1.4, 1.5, 1.6))
    print(buf1)

def test_030():
    buf1 = ListBuffer()
    buf1.capacity = 5
    buf1.install()
    buf1.push((1.0, 1.1, 1.2, 1.3, 1.4))
    print(buf1)
    print(buf1.data(3, True))
    print(buf1)
    print(buf1.data(3, False))
    print(buf1)


def test_add_strings_to_buffer():
    buf1 = ListBuffer()
    buf1.install()
    buf1.push("first")
    buf1.push("second")
    buf1.push("third")
    buf1.push("fourth")

    assert buf1.size() == 4
    assert buf1.data(4, True)[ "values"] == ["first", "second", "third", "fourth"]

def test_add_list_to_buffer():
    buf = ListBuffer()
    buf.install()
    buf.push([1, 2, 3])

    assert buf.size() == 3
    assert buf.data(3, True)["values"] == [1, 2, 3]

def test_add_dict_to_buffer():
    buf = ListBuffer()
    buf.install()
    d = {"a": 1, "b": 2, "c": 3}
    buf.push(d)

    assert buf.size() == 3
    assert buf.data(3, True)["values"] == [1, 2, 3]

def test_add_numpy_array_to_buffer():
    buf = ListBuffer()
    buf.install()
    arr = np.array([1, 2, 3])
    buf.push(arr)

    assert buf.size() == 1
    values = buf.data(1, True)["values"]
    assert len(values) == 1
    assert isinstance(values[0], np.ndarray)
    assert values[0].tolist() == [1, 2, 3]

def test_capacity_eviction_with_individual_pushes():
    buf = ListBuffer()
    buf.capacity = 3
    buf.install()
    buf.push(1)
    buf.push(2)
    buf.push(3)
    buf.push(4)

    assert buf.size() == 3
    assert buf.data(0, True)["values"] == [2, 3, 4]

def test_capacity_bulk_push_longer_than_capacity():
    buf = ListBuffer()
    buf.capacity = 3
    buf.install()
    buf.push([1, 2, 3, 4, 5])

    assert buf.size() == 3
    assert buf.data(0, True)["values"] == [3, 4, 5]

def test_capacity_with_numpy_arrays():
    buf = ListBuffer()
    buf.capacity = 2
    buf.install()
    buf.push(np.array([1]))
    buf.push(np.array([2]))
    buf.push(np.array([3]))

    assert buf.size() == 2
    vals = buf.data(0, True)["values"]
    assert len(vals) == 2
    assert isinstance(vals[0], np.ndarray) and isinstance(vals[1], np.ndarray)
    assert vals[0].tolist() == [2]
    assert vals[1].tolist() == [3]

def test_capacity_with_dict_conversion_bulk():
    buf = ListBuffer()
    buf.capacity = 3
    buf.install()
    d = {"a": 10, "b": 20, "c": 30, "d": 40}
    buf.push(d)

    assert buf.size() == 3
    assert buf.data(0, True)["values"] == [20, 30, 40]

def test_capacity_with_string_pushes():
    buf = ListBuffer()
    buf.capacity = 3
    buf.install()
    buf.push("first")
    buf.push("second")
    buf.push("third")
    buf.push("fourth")

    assert buf.size() == 3
    assert buf.data(0, True)["values"] == ["second", "third", "fourth"]


def test_infinite_capacity():
    buf = ListBuffer()
    buf.capacity = AgentKeywords.INFINITE_CAPACITY
    buf.install()
    buf.push([1, 2, 3, 4, 5])

    assert buf.size() == 5
    assert buf.data(0, True)["values"] == [1, 2, 3, 4, 5]
    
def test_with_dict_input():
    buf = ListBuffer()
    buf.install()
    dic = {"1": [1.0, 2.0]}
    buf.push(dic)
    
    d = buf.data()
    print(d)
    
    dic2 = {"1": 4.0}
    buf.push(dic2)
    
    d = buf.data()
    print(d)
    
    assert len(d["values"]) == 3, "return data has not the correct size"


def test_with_dict_input2():
    buf = ListBuffer()
    buf.install()
    dic = {"1": [1.0, 2.0], "2": [8.1, 7.3]}
    buf.push(dic)
    
    d = buf.data()
    print(d)
    
    dic2 = {"1": 4.0}
    buf.push(dic2)
    
    d = buf.data()
    print(d)
    
    assert len(d["values"]) == 5, "return data has not the correct size"