import os
from pydag.agents.Agent import Agent
from pydag.services.documents.ExcelBufferService import ExcelBufferService


def test_000():
    ag = Agent()
    
    excel_file = os.path.dirname(__file__) + os.sep + "Mappe1.xlsx"
    s = ExcelBufferService(excel_file=excel_file)
    
    s.install(ag)
    
    s.start()
    print(s._named_tables)
    for buf in ag._buffer_store.values():
        print(buf.data())
        
    s.stop()