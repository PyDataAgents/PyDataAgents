from dataclasses import dataclass, field
import pyodbc

from ...buffers.ListBuffer import ListBuffer
from ...adapters.AdapterException import AdapterException
from ...buffers.Buffer import Buffer
from ...buffers.DictBuffer import DictBuffer
from ...adapters.ReadAdapter import ReadAdapter
from ...adapters.WriteAdapter import WriteAdapter

@dataclass
class SQLAdapter(ReadAdapter, WriteAdapter):
    """`Adapter` for reading and writing data from/to SQL databases using pyodbc.
        <br>Required ODBC driver must be installed for the specific SQL database (e.g. MySQL, PostgreSQL, SQLite, etc.) and sytem
    """

    connection_str : str = field(default=None, metadata={"description": "connection string for the specific SQL database"})

    def __init__(self):
        super().__init__()
        self.connection = None
        self.cursor = None
        self.LOGGER.debug(pyodbc.drivers())

    def connect(self) -> bool:
        self.connection = pyodbc.connect(self.connection_str)
        if self.connection is None:
            return False
        else:
            self.cursor = self.connection.cursor()
            return True

    def disconnect(self) -> bool:
        self.cursor.close()
        self.connection.close()
        return True
        
    def read_from_source(self, buffers, addresses, n : int = 0):
        if len(buffers) == 1:
            for buffer in buffers:
                if isinstance(buffer, DictBuffer):
                    self.cursor.execute(addresses[0])
                    # fetch all results
                    results = self.cursor.fetchall()
                    # Get column names from cursor.description
                    columns = [column[0] for column in self.cursor.description]
                    # Convert each row to a dictionary {column_name: value}
                    data_with_columns = [dict(zip(columns, row)) for row in results]    
                    # push all rows to buffer
                    for row_dict in data_with_columns:
                        #print(row_dict)
                        buffer.push(row_dict)
                else:
                    raise AdapterException("buffers must be of type " + DictBuffer.cname())
        else:
            raise AdapterException("read_from_source is not supported for these inputs")

    def write_to_sink(self, buffers, addresses, n : int = 0, persistent : bool = True):
        """_summary_

        Args:
            buffers (dict[str, Buffer]): map of buffers to write data to sql database
            addresses (list[str]): list of addresses defining the database tables and columns to write to, the schema must adhere to table=<TABLE>;columns=<COLUMNS [comma separated lsit]>, if columns is left out, then all keys from DictBuffer are written or the id of ListBuffer is used for column selection
            n (int, optional): 
            persistent (bool, optional): _description_. Defaults to True.

        Raises:
            AdapterException: exception if a non-compliant input is specified
        """
        if len(buffers) == 1:
            for buffer in buffers:
                if isinstance(buffer, DictBuffer):
                    #TODO
                    data = buffer.data(n, persistent)
                    address = addresses[0]
                    if "columns=" in address:
                        #TODO
                        pass
                    else:
                        #TODO
                        pass                   
                elif isinstance(buffer, ListBuffer):
                    pass
                else:
                    raise AdapterException("buffers must be of type " + DictBuffer.cname())
        elif buffers is None and len(addresses) > 0:
            for address in addresses:
                if "create table" in address.lower():
                    self.cursor.execute(address)
                else:
                    raise AdapterException("only CREATE TABLE statements can be executed without specifying a " + Buffer.cname())
        else:
            raise AdapterException("write_to_sink is not supported for these inputs")