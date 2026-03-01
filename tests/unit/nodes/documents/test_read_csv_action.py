import os
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.documents.ReadCsvAction import ReadCsvAction


def test_000():    
    buf = DictBuffer()
    buf.id = "B1"
    buf.capacity = 10
    
    csv_action = ReadCsvAction()
    csv_action.file_path = os.path.dirname(__file__) + os.sep + "sample-data.csv"
    csv_action.set_buffer(buf)
    csv_action.install()
    
    csv_action.execute()
    
    d = buf.data()
    print(d)
    
    assert len(d.keys()) == 3, "wrong number of keys found in CSV"
    
    
    