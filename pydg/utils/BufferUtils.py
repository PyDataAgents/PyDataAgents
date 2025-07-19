from ..buffers.DictBuffer import DictBuffer
from ..buffers.Buffer import Buffer

class BufferUtils:
        
    @staticmethod    
    def to_dict(buffer : Buffer):
        d = {}
        d[buffer.id] = buffer
        return d
    
    @staticmethod
    def dict_buffer_to_html(dict_buffer : DictBuffer) -> str:
        
        DEFAULT_CELL_STYLE : str = "border: 1px solid black; border-collapse: collapse; padding: 5px";
        
        data = dict_buffer.data()
        # Transpose the data: get rows from column-based structure
        rows = zip(*data.values())
        columns = data.keys()
        # Start HTML table
        html = "<table border='1' style='" + DEFAULT_CELL_STYLE + "'>\n"

        # Add header row
        html += "  <tr>" + "".join(f"<th>{col}</th>" for col in columns) + "</tr>\n"

        # Add data rows
        for row in rows:
            html += "  <tr>" + "".join(f"<td>{val}</td>" for val in row) + "</tr>\n"

        html += "</table>"
        return html