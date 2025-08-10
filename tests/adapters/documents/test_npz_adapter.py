import numpy as np
from pydag.adapters.documents.NpzAdapter import NpzAdapter
from pydag.buffers.Buffer import Buffer
from pydag.buffers.DictBuffer import DictBuffer

def test_000():
    file_path = "tests\\data\\npz\\1730_Normal.npz"
    data = np.load(file_path)
    d = data["FE"]
    print(d)

def test_010():    
    file_path = "tests\\data\\npz\\1730_Normal.npz"    
    buf = DictBuffer(capacity=Buffer.INIFINITE_CAPACITY)    
    npz = NpzAdapter()
    