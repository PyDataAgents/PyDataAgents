import os
from pydag.nodes.documents.ReadExcelTableAction import ReadExcelTableAction


def test_000():
    
    a = ReadExcelTableAction(excel_file=os.path.dirname(__file__) + os.sep + "Mappe1.xlsx", table_name="TABLE1")
    
    a.install()
    
    a.execute()
    
    print(a._buffer.data())