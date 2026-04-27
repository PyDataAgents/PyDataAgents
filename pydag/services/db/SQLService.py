from dataclasses import dataclass, field
import re
from typing import Any
from loguru import logger
import pyodbc

from ..ReadService import ReadService
from ..WriteService import WriteService
from ..ServiceException import ServiceException


@dataclass
class SQLService(ReadService, WriteService):
    
    connection_str : str = field(default=None, metadata={"description": "connection string for the specific SQL database"})
    
    def __post_init__(self):
        super().__post_init__()
        self._conn = None
        self._cursor = None
    
    def _on_install(self, agent = None):
        super()._on_install(agent)
        self._conn = pyodbc.connect(self.connection_str)
        self._cursor = self._conn.cursor()
    
    def _on_uninstall(self, agent = None):
        super()._on_uninstall(agent)
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
                    
    def get_odbc_drivers(self) -> list[str]:
        """Returns the list of available ODBC drivers on the system

        Returns:
            list[str]: list of available ODBC drivers
        """
        return pyodbc.drivers()
    
    def _read_from_source(self):
        """_summary_

        Args:
            buffers (_type_): dict of `Buffer`s to store the query result
            addresses (list[str]): addresses can be used to specify SELECT querys
            n (int, optional): Number of samples. Defaults to 0.

        Raises:
            ServiceException: if Buffer is not supported or inputs are not correct
        """
        it = iter(self.addresses)
        for buffer in self.get_buffers().values():
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

    def _write_to_sink(self):
        """writes data from buffer to SQL database

        Args:
            buffers (dict[str, Buffer]): map of buffers to write data to sql database
            addresses (list[str]): list of SQL statements for UPDATE or INSERT
            n (int, optional): 
            persistent (bool, optional): _description_. Defaults to True.

        Raises:
            AdapterException: exception if a non-compliant input is specified
        """
        if len(self.get_buffers()) == len(self.addresses):
            it = iter(self.addresses)
            for buffer in self.get_buffers().values():
                address = next(it)
                data = buffer.data(n=self.n, persistent=self.persistent)
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
                                raise ServiceException("unsupported combination of buffer content and address")
                    
                        #self._cursor.executemany(address, tuple_data) # TODO why is batch upload not working
                        for tu in tuple_data:
                            try:
                                self._cursor.execute(address, tu)
                                self._conn.commit()
                            except Exception as e:
                                self._conn.rollback() # resetting transaction before anything else
                                if "UNIQUE constraint failed" in str(e):
                                    logger.error("could not execute SQL\n\t" + str(e))
                                else:
                                    raise ServiceException("could not execute SQL " + address + " with data " + str(tu) + "\n\t" + str(e))
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
                                raise ServiceException("unsupported combination of buffer content and address")
                        
                        #self._cursor.executemany(address, tuple_data) # TODO why is batch upload not working
                        for tu in tuple_data:
                            try:
                                self._cursor.execute(address, tu)
                                self._conn.commit()
                            except Exception as e:
                                self._conn.rollback() # resetting transaction before anything else
                                if "UNIQUE constraint failed" in str(e):
                                    logger.error("could not execute SQL\n\t" + str(e))
                                else:
                                    raise ServiceException("could not execute SQL " + address + " with data " + tu)
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
                                raise ServiceException("unsupported combination of buffer content and address")
                        #self._cursor.executemany(address, tuple_data) # TODO why is batch upload not working
                        for tu in tuple_data:
                            self._cursor.execute(address, tu)
                            self._conn.commit()
                elif "create table" in address.lower():
                    self._cursor.execute(address)
                    self._conn.commit()
                elif "alter table" in address.lower():
                    self._cursor.execute(address)
                    self._conn.commit()
                elif "drop table" in address.lower():
                    self._cursor.execute(address)
                    self._conn.commit()
                else:
                    raise ServiceException("unsupported SQL statement, only INSERT or UPDATE is supported")
        elif len(self.addresses) > 0:
            # check for create table statements, does not require a buffer
            for address in self.addresses:
                if "create table" in address.lower():
                    self._cursor.execute(address)
                if "alter table" in address.lower():
                    self._cursor.execute(address)
                elif "drop table" in address.lower():
                    self._cursor.execute(address)
                elif "delete from" in address.lower():
                    self._cursor.execute(address)
            
                self._conn.commit()
    
    def fetch(self, select = "*", from_ = None, where = None, order=None) -> list[dict]:
        """Fetch data from the SQL database

        Args:
            select (str, optional): SELECT part of the query. Defaults to "*".
            from_ (str, optional): FROM part of the query. Defaults to None.
            where (str, optional): WHERE part of the query. Defaults to None.
            order (str, optional): ORDER BY part of the query. Defaults to None.

        Returns:
            list[dict]: list of rows as dictionaries
        """
        query = f"SELECT {select} FROM {from_}"
        if where:
            query += f" WHERE {where}"
        if order:
            query += f" ORDER BY {order}"
        
        self._cursor.execute(query)
        results = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        data_with_columns = [dict(zip(columns, row)) for row in results]
        return data_with_columns
    
    def insert(self, into: str, values: dict) -> int:
        """Insert data into the SQL database

        Args:
            into (str): table name
            values (dict): dictionary of column names and values to insert

        Returns:
            int: number of rows inserted
        """
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?'] * len(values))
        query = f"INSERT INTO {into} ({columns}) VALUES ({placeholders})"
        self._cursor.execute(query, tuple(values.values()))
        self._conn.commit()
        return self._cursor.rowcount
    
    def update(self, table: str, values: dict, where: str) -> int:
        """Update data in the SQL database

        Args:
            table (str): table name
            values (dict): dictionary of column names and new values
            where (str): WHERE clause to specify which rows to update

        Returns:
            int: number of rows updated
        """
        set_clause = ', '.join([f"{col} = ?" for col in values.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        self._cursor.execute(query, tuple(values.values()))
        self._conn.commit()
        return self._cursor.rowcount
    
    def execute(self, query: str) -> Any:
        """Execute a custom SQL query

        Args:
            query (str): SQL query to execute
        """
        self._cursor.execute(query)
        self._conn.commit()
        results = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        data_with_columns = [dict(zip(columns, row)) for row in results]
        return data_with_columns

