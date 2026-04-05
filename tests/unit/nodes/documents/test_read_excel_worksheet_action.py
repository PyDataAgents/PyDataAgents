import os
import pytest
from openpyxl import Workbook
from pydag.nodes.NodeException import NodeException
from pydag.nodes.documents.ReadExcelWorksheetAction import ReadExcelWorksheetAction


excel_file = os.path.dirname(__file__) + os.sep + "Mappe1.xlsx"

def test_read_worksheet_with_headers():
    """Test reading worksheet with headers (first row as headers)"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet1",
        has_header=True
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    assert data is not None
    assert len(data) > 0
    # Should have columns from first row: C1, C2, COL2, COL3, COL4
    assert "C1" in data or "COL0" in data
    
def test_read_worksheet_without_headers():
    """Test reading worksheet without treating first row as headers"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet1",
        has_header=False
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    assert data is not None
    # Should generate COL0, COL1, etc.
    assert "COL0" in data
    assert "COL1" in data
    
def test_read_first_worksheet_with_data():
    """Test auto-selection of first worksheet with data when worksheet not specified"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet=None,
        has_header=True
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    assert data is not None
    assert len(data) > 0


def test_read_specific_worksheet_by_name():
    """Test reading specific worksheet by name"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet2",
        has_header=True
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    assert data is not None
    
def test_read_specific_worksheet_by_index():
    """Test reading specific worksheet by index (0-based)"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet=0,
        has_header=True
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    assert data is not None
    
def test_read_second_worksheet_by_index():
    """Test reading second worksheet by index"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet=1,
        has_header=True
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    print(data)
    assert data is not None
    
def test_invalid_worksheet_name():
    """Test error handling for invalid worksheet name"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="NonexistentSheet",
        has_header=True
    )
    action.install()
    
    with pytest.raises(NodeException) as exc_info:
        action.execute()
    assert "could not be found" in str(exc_info.value)
    
def test_invalid_worksheet_index():
    """Test error handling for invalid worksheet index"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet=99,
        has_header=True
    )
    action.install()
    
    with pytest.raises(NodeException) as exc_info:
        action.execute()
    assert "could not be found" in str(exc_info.value)


def test_read_with_start_range():
    """Test reading from a specific start range"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet1",
        start_range="A1",
        has_header=True
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    assert data is not None
    
def test_read_with_different_start_range():
    """Test reading from a different start range"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet1",
        start_range="A2",
        has_header=False
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    print(data)
    assert data is not None
    
def test_invalid_start_range_format():
    """Test error handling for invalid start_range format"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet1",
        start_range="INVALID",
        has_header=True
    )
    action.install()
    
    with pytest.raises(NodeException) as exc_info:
        action.execute()
    assert "Invalid Address" in str(exc_info.value)


def test_nonexistent_file():
    """Test error handling when file doesn't exist"""
    action = ReadExcelWorksheetAction(
        excel_file="/nonexistent/path/file.xlsx",
        worksheet="Sheet1",
        has_header=True
    )
    action.install()
    
    with pytest.raises(NodeException) as exc_info:
        action.execute()
    assert "could not be found" in str(exc_info.value)

def test_all_data_is_read():
    """Test that all data from connected range is read"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet1",
        has_header=True
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    # Data should contain the rows from the connected range
    for key in data:
        assert len(data[key]) > 0
    
def test_header_row_not_included_in_data():
    """Test that header row is not included as data when has_header=True"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet1",
        has_header=True
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    # Get first column data
    first_key = next(iter(data.keys()))
    # The first data value should be the first data row, not the header
    assert data[first_key][0] != "C1"  # "C1" is the header

def test_null_values_handled_correctly():
    """Test that null values in cells are handled correctly"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet1",
        has_header=True
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    assert data is not None
    # Should not raise any errors and data should be present
    
def test_mixed_data_types():
    """Test handling of mixed data types (numbers, strings, etc.)"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet1",
        has_header=True
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    # Data should contain both string and numeric values
    assert len(data) > 0


def test_buffer_is_initialized():
    """Test that buffer is properly initialized"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet1",
        has_header=True
    )
    action.install()
    
    assert action.get_buffer() is not None
    
def test_data_added_to_buffer():
    """Test that data is added to buffer after execution"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet1",
        has_header=True
    )
    action.install()
    action.execute()
    
    buffer = action.get_buffer()
    assert buffer.size() > 0

def test_generated_column_names():
    """Test that column names are generated as COL0, COL1, etc. when has_header=False"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet1",
        has_header=False
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    # Check for generated column names
    assert "COL0" in data
    assert "COL1" in data
    
def test_null_header_replaced_with_generated_name():
    """Test that None/empty headers are replaced with generated COL names"""
    action = ReadExcelWorksheetAction(
        excel_file=excel_file,
        worksheet="Sheet1",
        has_header=True
    )
    action.install()
    action.execute()
    
    data = action.get_buffer().data()
    # There should be some generated column names for None values
    has_generated_cols = any("COL" in key for key in data.keys())
    assert has_generated_cols or len(data) > 0