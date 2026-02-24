from dataclasses import dataclass, field
import re
import pyodbc

from loguru import logger


from ...agents import Agent
from ...adapters.AdapterException import AdapterException
from ...adapters.ReadAdapter import ReadAdapter
from ...adapters.WriteAdapter import WriteAdapter

@dataclass
class SQLAdapter(ReadAdapter, WriteAdapter):
    """ `Adapter` for reading and writing data from/to SQL databases using pyodbc.
        <br>Required ODBC driver must be installed for the specific SQL database (e.g. MySQL, PostgreSQL, SQLite, etc.) and system
        <br><br>The `addresses` in `_on_write` and `_on_read` is used to specify the SQL statement to execute. SQL statements should adhere the following format:
        - SELECT: 'SELECT [column1], [column2], ... FROM [table] WHERE [column3] = [value1]'
        - CREATE TABLE: 'CREATE TABLE ...'        
        - INSERT: 'INSERT INTO [table] ([column1], [column2], [column3], ...) VALUES (?, ?, ?, ...)'
        - UPDATE: 'UPDATE [table] SET [column1] = ?, [column2] = ?, ... WHERE [column3] = ?'
        - DELETE: 'DELETE FROM [table] WHERE [column1] = ? AND [column2] = ? OR ...'
        - ALTER: 'ALTER TABLE [table] ADD COLUMN [column1] [datatype] {DEFAULT [value]}'
        - DROP: 'DROP TABLE [table]'
    """

    connection_str : str = field(default=None, metadata={"description": "connection string for the specific SQL database"})

    def __post_init__(self):
        super().__post_init__()
        self._connection = None
        self._cursor = None

    def _on_install(self, agent : Agent = None):
        if self.connection_str is None:
            raise AdapterException("No connection string was specified for " + self.cname())        
        logger.debug(pyodbc.drivers())
        
    def _on_uninstall(self, agent : Agent = None):
        self._connection = None
        self._cursor = None

    def _on_connect(self) -> bool:
        self._connection = pyodbc.connect(self.connection_str)
        if self._connection is None:
            return False
        else:
            self._cursor = self._connection.cursor()
            self._cursor.fast_executemany = True                        
            return True

    def _on_disconnect(self) -> bool:
        if self._cursor:
            self._cursor.close()
        if self._connection:
            self._connection.close()
        return True
        
    def _on_read(self, buffers, addresses, n : int = 0):
        """_summary_

        Args:
            buffers (_type_): dict of `Buffer`s to store the query result
            addresses (list[str]): addresses can be used to specify SELECT querys
            n (int, optional): Number of samples. Defaults to 0.

        Raises:
            AdapterException: if Buffer is not supported or inputs are not correct
        """
        it = iter(addresses)
        for buffer in buffers.values():
            address = next(it)
            self._cursor.execute(address)
            # fetch all results
            results = self._cursor.fetchall()
            # Get column names from cursor.description
            columns = [column[0] for column in self._cursor.description]
            # Convert each row to a dictionary {column_name: value}
            data_with_columns = [dict(zip(columns, row)) for row in results]    
            # push all rows to buffer
            for row_dict in data_with_columns:
                #print(row_dict)
                buffer.push(row_dict)

    def _on_write(self, buffers, addresses, n : int = 0, persistent : bool = True):
        """writes data from buffer to SQL database

        Args:
            buffers (dict[str, Buffer]): map of buffers to write data to sql database
            addresses (list[str]): list of SQL statements for UPDATE or INSERT
            n (int, optional): 
            persistent (bool, optional): _description_. Defaults to True.

        Raises:
            AdapterException: exception if a non-compliant input is specified
        """
        if len(buffers) == len(addresses):
            it = iter(addresses)
            for buffer in buffers.values():
                address = next(it)
                data = buffer.data(n, persistent)
                data_keys = data.keys()
                if "insert into" in address.lower():
                    # extract columns from INSERT statement
                    match = re.search(r"INSERT\s+INTO\s+\w+\s*\(([^)]+)\)", address, re.IGNORECASE)
                    if match:
                        insert_keys = [c.strip() for c in match.group(1).split(",")]
                        #print(insert_keys)                 
                        if set(insert_keys).issubset(data_keys):
                            ordered_data = dict()
                            for insert_key in insert_keys:
                                ordered_data[insert_key] = data[insert_key]
                            tuple_data = list(zip(*ordered_data.values())) 
                        else:                        
                            if len(insert_keys) == len(data_keys):
                                tuple_data = list(zip(*data.values()))  
                            else:
                                raise AdapterException("unsupported combination of buffer content and address")
                    
                        #self._cursor.executemany(address, tuple_data) # TODO why is batch upload not working
                        for tu in tuple_data:
                            try:
                                self._cursor.execute(address, tu)
                                self._connection.commit()
                            except Exception as e:
                                self._connection.rollback() # resetting transaction before anything else
                                if "UNIQUE constraint failed" in str(e):
                                    logger.error("could not execute SQL\n\t" + str(e))
                                else:
                                    raise AdapterException("could not execute SQL " + address + " with data " + str(tu) + "\n\t" + str(e))
                elif "update" in address.lower():
                    # extract columns from sql statement
                    match = re.search(r"SET\s+(.+?)(\s+WHERE|;|$)", address, re.IGNORECASE | re.DOTALL)
                    if match:
                        columns_part = match.group(1)
                        # Split by commas and extract column names before '='
                        update_keys = [col.split('=')[0].strip() for col in columns_part.split(',')]
                        #print(insert_keys)
                        if set(update_keys).issubset(data_keys):
                            ordered_data = {}
                            for update_key in update_keys:
                                ordered_data[update_key] = data[update_key]
                            tuple_data = list(zip(*ordered_data.values())) 
                        else:                        
                            if len(update_keys) == len(data_keys):
                                tuple_data = list(zip(*data.values()))
                            else:
                                raise AdapterException("unsupported combination of buffer content and address")
                        
                        #self._cursor.executemany(address, tuple_data) # TODO why is batch upload not working
                        for tu in tuple_data:
                            try:
                                self._cursor.execute(address, tu)
                                self._connection.commit()
                            except Exception as e:
                                self._connection.rollback() # resetting transaction before anything else
                                if "UNIQUE constraint failed" in str(e):
                                    logger.error("could not execute SQL\n\t" + str(e))
                                else:
                                    raise AdapterException("could not execute SQL " + address + " with data " + tu)
                elif "delete from" in address.lower():
                    # Capture everything after WHERE
                    where_clause_match = re.search(r"WHERE\s+(.+?)(;|$)", address, re.IGNORECASE | re.DOTALL)
                    if where_clause_match:
                        where_clause = where_clause_match.group(1)
                        # Split by AND / OR
                        conditions = re.split(r"\s+AND\s+|\s+OR\s+", where_clause, flags=re.IGNORECASE)
                        # Extract column names (assumes simple 'column operator value')
                        where_keys = [re.match(r"([a-zA-Z_][a-zA-Z0-9_]*)", cond.strip()).group(1) for cond in conditions]
                        #print(where_keys)
                        if set(where_keys).issubset(data_keys):
                            ordered_data = {}
                            for where_key in where_keys:
                                ordered_data[where_key] = data[where_key]
                            tuple_data = list(zip(*ordered_data.values())) 
                        else:
                            if len(where_keys) == len(data_keys):
                                tuple_data = list(zip(*data.values()))
                            else:
                                raise AdapterException("unsupported combination of buffer content and address")
                        #self._cursor.executemany(address, tuple_data) # TODO why is batch upload not working
                        for tu in tuple_data:
                            self._cursor.execute(address, tu)
                            self._connection.commit()
                elif "create table" in address.lower():
                    self._cursor.execute(address)
                    self._connection.commit()
                elif "alter table" in address.lower():
                    self._cursor.execute(address)
                    self._connection.commit()
                elif "drop table" in address.lower():
                    self._cursor.execute(address)
                    self._connection.commit()
                else:
                    raise AdapterException("unsupported SQL statement, only INSERT or UPDATE is supported")
        elif len(addresses) > 0:
            # check for create table statements, does not require a buffer
            for address in addresses:
                if "create table" in address.lower():
                    self._cursor.execute(address)
                if "alter table" in address.lower():
                    self._cursor.execute(address)
                elif "drop table" in address.lower():
                    self._cursor.execute(address)
                elif "delete from" in address.lower():
                    self._cursor.execute(address)
            
                self._connection.commit() 
           