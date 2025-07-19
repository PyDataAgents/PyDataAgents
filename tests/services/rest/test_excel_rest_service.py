import os
from pydg.services.rest.ExcelRestService import ExcelRestService


def test_000():
    s = ExcelRestService()
    s.excel_file = os.path.dirname(__file__) + os.sep + "Mappe1.xlsx"
    s.install()
    for db in s.named_tables.values():
        print(db.data())