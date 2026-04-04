import os

import pytest
from pydag.nodes.NodeException import NodeException
from pydag.nodes.documents.ReadExcelRangeAction import ReadExcelRangeAction

excel_file = os.path.dirname(__file__) + os.sep + "Mappe1.xlsx"

def test_read_range():
    
    rera = ReadExcelRangeAction(excel_file=excel_file, worksheet="Sheet1", range="A1:B3", has_header=False)
    rera.install()
    rera.execute()
    data = rera.get_buffer().data()
    print(data)  
    assert len(next(iter(data.values()))) == 3
    
def test_named_range():
    rera = ReadExcelRangeAction(excel_file=excel_file, worksheet="Sheet2", range="TABLE2", has_header=True)
    rera.install()
    rera.execute()
    data = rera.get_buffer().data()
    print(data)
    assert len(next(iter(data.values()))) == 4
    
def test_no_range_specified():
    rera = ReadExcelRangeAction(excel_file=excel_file, worksheet="Sheet1", has_header=False)
    rera.install()
    with pytest.raises(NodeException):
        rera.execute()
    
def test_range_with_missing_values():
    rera = ReadExcelRangeAction(excel_file=excel_file, worksheet="Sheet1", range="E2:E10", has_header=False)
    rera.install()
    rera.execute()
    data = rera.get_buffer().data()    
    print(data)
    assert len(next(iter(data.values()))) == 9
    
def test_wrong_worksheet():
    rera = ReadExcelRangeAction(excel_file=excel_file, worksheet="WrongSheet", range="A1:B3", has_header=False)
    rera.install()
    with pytest.raises(NodeException):
        rera.execute()
        
def test_wrong_workbook():
    rera = ReadExcelRangeAction(excel_file="nonexistent.xlsx", worksheet="Sheet1", range="A1:B3", has_header=False)
    rera.install()
    with pytest.raises(NodeException):
        rera.execute()
    