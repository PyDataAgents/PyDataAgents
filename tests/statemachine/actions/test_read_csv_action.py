import os
from pydg.buffers.DictBuffer import DictBuffer
from pydg.statemachine.actions.documents.ReadCsvAction import ReadCsvAction


def test_000():
    print(os.getcwd())
    
    buf = DictBuffer()
    buf.id = "B1"
    buf.capacity = 10
    
    csv_action = ReadCsvAction()
    csv_action.file_path = os.getcwd() + "\\tests\\data\\test.csv"
    csv_action.buffer = buf
    
    csv_action.execute()
    
    print(buf.data())
    
    
    