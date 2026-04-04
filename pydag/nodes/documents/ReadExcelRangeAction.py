from dataclasses import dataclass, field
from typing import Union

from openpyxl import load_workbook
#from openpyxl.worksheet.table import Table

from ..NodeException import NodeException
from ...utils.FileUtils import FileUtils
from ..Action import Action
from ..BufferNode import BufferNode

@dataclass
class ReadExcelRangeAction(BufferNode, Action):
    """ This `Action` reads data from specified workbook, worksheet and range

    Args:
        BufferNode (_type_): _description_
        Action (_type_): _description_

    Raises:
        NodeException: _description_
    """
    
    excel_file : str = field(default=None, metadata={"description": "path to the excel files to read the range from"})
    worksheet : Union[str | int] = field(default=None, metadata={"description": "name of the worksheet inside the excel to read from or the index of the worksheet starting with 0 for the first worksheet"})
    range : str = field(default=None, metadata={"description": "address of the range in the worksheet inside the excel to read from"})
    has_header : bool = field(default=False, metadata={"description": "specifies whether the first row in range contains header descriptions"})
        
    def _on_execute(self):
        if FileUtils.exists_file(self.excel_file):
            # Load the workbook
            wb = load_workbook(self.excel_file, data_only=True)
            try:
                ws = wb[self.worksheet]
            except IndexError as e:
                raise NodeException("the specified worksheet " + self.worksheet + " could not be found in the excel file " + self.excel_file) from e
            except KeyError as e:
                raise NodeException("the specified worksheet " + self.worksheet + " could not be found in the excel file " + self.excel_file) from e
            if self.range is None:
                raise NodeException("no range was specified to read from, please specify a range or a named table to read from")
            cells = None
            try:
                cells = ws[self.range]
            except ValueError:
                for table_name, table_range in ws.tables.items():
                    if table_name == self.range:
                        cells = ws[table_range]
                        break
            if cells is None:
                raise NodeException("the specified range " + self.range + " could not be found in worksheet " + self.worksheet)
            r = 0
            headers = []
            for row in cells:
                #print([cell.value for cell in row]) 
                if r == 0 and self.has_header:
                    headers = [cell.value for cell in row]                    
                    r = r + 1
                    continue
                elif r == 0:
                    headers = [f'COL{i}' for i in range(len(row))]
                d = dict()
                h = 0
                for cell in row:
                    d[headers[h]] = cell.value
                    h = h + 1
                self.add_data(d)                
                r = r + 1
        else:
            raise NodeException("the file " + self.excel_file + " could not be found")