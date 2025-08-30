from __future__ import annotations
from dataclasses import dataclass, field
from fastapi import FastAPI
from openpyxl import load_workbook
import pandas as pd

from ..ServiceException import ServiceException
from ...utils.FileUtils import FileUtils
from ...buffers.DictBuffer import DictBuffer
from ..Service import Service
from ...agents.Agent import Agent


@dataclass
class ExcelBufferService(Service):
    """`Service` for creating a REST API for accessing named Tables in Excel
    """
    
    excel_file : str = field(default=None, metadata={"description" : "path of the excel file to open for tables"})
           
    def __post_init__(self):
        super().__post_init__()
        self.named_tables : list[str] = []
        
    def start(self):
        super().start()
        if self.agent is None:
            raise ServiceException("No " + Agent.cname() + " was specified, make sure to install the " + self.cname() + " before starting!")
        if FileUtils.exists_file(self.excel_file):
            # Load the workbook
            wb = load_workbook(self.excel_file, data_only=True)
            for ws in wb.worksheets:
                for table_name, table_range in ws.tables.items():
                    #print("🧾 Table name:", table_name)
                    #print("📐 Range:", table_range)
                    # Access the cells inside the table range
                    #print(type(table_range))
                    cells = ws[table_range]
                    dbuf = DictBuffer(id=table_name, capacity=len(cells))
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
                            dbuf.push(d)
                        r = r + 1
                    self.agent.add_buffer(dbuf)
                    self.named_tables.append(dbuf.id)
        else:
            raise ServiceException("the file " + self.excel_file + " could not be found")
    
    def stop(self):
        super().stop()
        self.named_tables = []
        
    def to_dataframes(self) -> dict[str, pd.DataFrame]:
        """Returns a dictionary of pandas DataFrames for each named table in the excel file

        Returns:
            dict[str, pd.DataFrame]: dictionary of DataFrames
        """
        dfs : dict[str, pd.DataFrame] = dict()
        for name in self.named_tables:
            buf = self.agent.get_buffer(name)
            dfs[name] = pd.DataFrame(buf.data())
        return dfs