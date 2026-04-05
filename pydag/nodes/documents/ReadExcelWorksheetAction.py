from dataclasses import dataclass, field
from typing import Tuple, Union

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
from openpyxl.utils import get_column_letter, range_boundaries

from ..NodeException import NodeException
from ...utils.FileUtils import FileUtils
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class ReadExcelWorksheetAction(BufferNode, Action):
    """This `BufferNode` reads the entire content of a specified Excel worksheet into a buffer.
    
    It automatically detects the first worksheet with data if no specific worksheet is specified,
    finds the connected range of data, and uses the first row as headers by default.
    
    Args:
        BufferNode: Provides buffer management functionality
        Action: Provides action execution framework
        
    Raises:
        NodeException: If file not found, worksheet not found, or no data found in worksheet
    """
    
    excel_file: str = field(default=None, metadata={"description": "Path to the Excel file to read from"})
    worksheet: Union[str, int] = field(default=None, metadata={"description": "Name (str) or index (int, 0-based) of the worksheet. If None, reads from first worksheet with data"})
    start_range: str = field(default=None, metadata={"description": "Cell address to start reading from (e.g., 'A1'). If None, auto-detects the first connected data range"})
    has_header: bool = field(default=True, metadata={"description": "If True, treats first row as column headers. If False, generates COL0, COL1, etc."})
    
    def _find_first_filled_cell(self, ws : Worksheet) -> Cell:
        if ws.dimensions:  # Has data
            dim_str : str = ws.dimensions
            start_range = dim_str.split(":")[0]
            return ws[start_range]
        else:
            raise NodeException(f"Could not find any data in Worksheet {ws.title}")
    
    def _find_connected_range(self, ws: Worksheet, start_cell : Cell) -> tuple[int, int, int, int]:
        start_row = start_cell.row
        start_col = start_cell.column

        # 1. Find rightmost column (continuous block)
        col = start_col
        while ws.cell(row=start_row, column=col).value is not None:
            col += 1
        end_col = col - 1

        # 2. For each column, find last filled row downward
        end_row = 0
        for col in range(start_col, end_col + 1):
            row = start_row
            while ws.cell(row=row, column=col).value is not None:
                row += 1
            if end_row < row - 1:
                end_row = row - 1

        return (start_row, start_col, end_row, end_col)
    
    def _select_worksheet(self, wb : Workbook) -> Worksheet:
        """Select the appropriate worksheet.
        
        Args:
            wb: The openpyxl workbook object
            
        Returns:
            tuple: (worksheet, worksheet_name)
            
        Raises:
            NodeException: If specified worksheet not found or no worksheet with data found
        """
        if self.worksheet is not None:
            # Worksheet is explicitly specified
            try:
                if isinstance(self.worksheet, int):
                    ws : Worksheet = wb.worksheets[self.worksheet]
                else:
                    ws = wb[self.worksheet]
                return ws
            except (IndexError, KeyError) as e:
                raise NodeException(f"Worksheet '{self.worksheet}' could not be found in {self.excel_file}") from e
        else:
            # Find first worksheet with data
            for ws in wb.worksheets:
                if ws.dimensions:  # Has data
                    return ws
            
            # If no dimensions, check by scanning
            for ws in wb.worksheets:
                for row in ws.iter_rows():
                    for cell in row:
                        if cell.value is not None:
                            return ws
            
            raise NodeException(f"No worksheet with data found in {self.excel_file}")
    
    def _read_data_range(self, ws : Worksheet, start_row : int, start_col : int, end_row : int, end_col : int):
        """Read data from the specified range and add to buffer.
        
        Args:
            ws: The openpyxl worksheet object
            start_row: Starting row (1-based)
            start_col: Starting column (1-based)
            end_row: Ending row (1-based)
            end_col: Ending column (1-based)
        """
        headers = []
        
        for row_idx, row in enumerate(
            ws.iter_rows(
                min_row=start_row,
                max_row=end_row,
                min_col=start_col,
                max_col=end_col,
                values_only=True
            )
        ):
            if row_idx == 0:
                # First row - treat as headers or generate column names
                if self.has_header:
                    headers = [header if header is not None else f"COL{i}" for i, header in enumerate(row)]
                else:
                    headers = [f"COL{i}" for i in range(len(row))]
            else:
                # Data rows
                data_dict = {}
                for col_idx, value in enumerate(row):
                    if col_idx < len(headers):
                        data_dict[headers[col_idx]] = value
                
                self.add_data(data_dict)
    
    def _on_execute(self):
        """Execute the action to read the entire Excel worksheet into the buffer."""
        if not FileUtils.exists_file(self.excel_file):
            raise NodeException(f"File {self.excel_file} could not be found")
        
        # Load the workbook
        wb : Workbook = load_workbook(self.excel_file, data_only=True)
        
        # Select the appropriate worksheet
        ws : Worksheet = self._select_worksheet(wb)
        
        # Determine the data range to read
        if self.start_range is not None:
            # Start from specified range
            try:
                start_cell : Cell = ws[self.start_range]
                start_row, start_col, end_row, end_col = self._find_connected_range(ws, start_cell)
            except ValueError as e:
                raise NodeException("Invalid Address for start_range") from e
        else:
            start_cell = self._find_first_filled_cell(ws)
            start_row, start_col, end_row, end_col = self._find_connected_range(ws, start_cell)
                      
        # Read the data from the range
        self._read_data_range(ws, start_row, start_col, end_row, end_col)
        
        wb.close()
