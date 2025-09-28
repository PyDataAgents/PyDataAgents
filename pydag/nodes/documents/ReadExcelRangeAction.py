from dataclasses import dataclass, field

from openpyxl import load_workbook
#from openpyxl.worksheet.table import Table

from ..NodeException import NodeException
from ...utils.FileUtils import FileUtils
from ..Action import Action
from ..BufferNode import BufferNode

@dataclass
class ReadExcelRangeAction(BufferNode, Action):
    
    excel_file : str = field(default=None, metadata={"description": "path to the excel files to read the range from"})
    worksheet : str = field(default=None, metadata={"description": "name of the worksheet inside the excel to read from"})
    range : str = field(default=None, metadata={"description": "address of the range in the worksheet inside the excel to read from"})
    has_header : bool = field(default=False, metadata={"description": "specifies whether the first row in range contains header descriptions"})
        
    def execute(self):
        if FileUtils.exists_file(self.excel_file):
            # Load the workbook
            wb = load_workbook(self.excel_file, data_only=True)
            ws = wb[self.worksheet]
            cells = ws[self.range]
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
                self.buffer.push(d)                
                r = r + 1
        else:
            raise NodeException("the file " + self.excel_file + " could not be found")