import os
from pydag.agents.Agent import Agent
from pydag.services.documents.ExcelBufferService import ExcelBufferService


def test_000():
    ag = Agent()
    s = ExcelBufferService()
    s.agent = ag
    s.excel_file = os.path.dirname(__file__) + os.sep + "Mappe1.xlsx"
    s.install()
    s.start()
    print(s.named_tables)
    for buf in ag.buffer_store.values():
        print(buf.data())
        
    s.stop()