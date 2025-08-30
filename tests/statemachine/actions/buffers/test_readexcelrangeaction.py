import os
from pydag.statemachine.actions.documents.ReadExcelRangeAction import ReadExcelRangeAction


def test_000():
    
    a = ReadExcelRangeAction(excel_file=os.path.dirname(__file__) + os.sep + "Mappe1.xlsx", worksheet="Tabelle1", range="A1:B3", has_header=True)
    
    a.install()
    
    a.execute()
    
    print(a.buffer.data())