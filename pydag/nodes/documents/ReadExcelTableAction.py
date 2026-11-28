from dataclasses import dataclass, field

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.worksheet.table import Table

from ..NodeException import NodeException
from ...utils.FileUtils import FileUtils
from ..Action import Action
from ..BufferNode import BufferNode

@dataclass
class ReadExcelTableAction(BufferNode, Action):
    
    excel_file : str = field(default=None, metadata={"description": "path to the excel files to read named table from"})
    table_name : str = field(default=None, metadata={"description": "name of the table inside the excel to read from"})
    sheet_name : str = field(default=None, metadata={"description": "name of the sheet, can be specified optionally"})
        
    def _on_execute(self):
        if FileUtils.exists_file(self.excel_file):
            # Load the workbook
            wb = load_workbook(self.excel_file, data_only=True)
            ws : Worksheet = None
            if self.sheet_name:
                ws = wb[self.sheet_name]
            else:                
                for sh in wb.worksheets:
                    if self.table_name in sh.tables:
                        ws = sh
                        break
            if ws:
                t_range : Table = ws.tables[self.table_name]
                #print("🧾 Table name:", table_name)
                #print("📐 Range:", table_range)
                # Access the cells inside the table range                    
                cells = ws[t_range.ref]
                r = 0
                headers = []
                for row in cells:
                    #print([cell.value for cell in row]) 
                    if r == 0:
                        headers = [cell.value for cell in row]
                    else:
                        d = dict()
                        h = 0
                        for cell in row:
                            d[headers[h]] = cell.value
                            h = h + 1
                        self.add_data(d)
                    r = r + 1
            else:
                raise NodeException("No worksheet with named table '" + self.table_name + "' could be found")
        else:
            raise NodeException("the file " + self.excel_file + " could not be found")