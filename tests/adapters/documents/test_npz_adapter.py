import numpy as np
from pydag.adapters.documents.NpzAdapter import NpzAdapter
from pydag.buffers.Buffer import Buffer
from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.ListBuffer import ListBuffer
from pydag.utils.BufferUtils import BufferUtils
from pydag.utils.DataUtils import DataUtils

def test_000():
    file_path = "tests\\data\\npz\\1730_Normal.npz"
    data = np.load(file_path)
    d = data["FE"]
    dd = DataUtils.ndarray_to_dict(d)
    dl = DataUtils.ndarray_to_list(d)
    df = d.flatten()
    print(dd)
    print(dl)    
    print(df)

def test_010():    
    file_path = "tests\\data\\npz\\1730_Normal.npz"    
    buf = DictBuffer(capacity=Buffer.INFINITE_CAPACITY)    
    
    npz = NpzAdapter(file_path=file_path)
    
    buffers = BufferUtils.to_dict(buf)
    
    addresses = []
    
    npz.connect()
    
    npz.read_from_source(buffers, addresses)
    
    print(buf.data(n=100))
    
def test_011():    
    file_path = "tests\\data\\npz\\1730_Normal.npz"    
    buf1 = ListBuffer(capacity=Buffer.INFINITE_CAPACITY)    
    buf2 = ListBuffer(capacity=Buffer.INFINITE_CAPACITY)    
    
    npz = NpzAdapter(file_path=file_path)
    
    buffers = BufferUtils.to_dict(buf1)
    buffers[buf2.id] = buf2
    
    addresses = ["FE", "DE"]
    
    npz.connect()
    
    npz.read_from_source(buffers, addresses)
    
    print(buf1.data())
    print(buf2.data())
    