import os

from pydag.nodes.documents.ReadExcelTableAction import ReadExcelTableAction


def test_read_named_excel_table():
    fp : str = os.path.dirname(__file__) + os.sep + "Mappe1.xlsx"
    reta = ReadExcelTableAction(excel_file=fp, table_name="TABLE1")
    reta.install()
    reta.execute()
    print(reta.get_data())