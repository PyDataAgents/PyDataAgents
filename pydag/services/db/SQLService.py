from dataclasses import dataclass, field
from typing import Any
import pyodbc
from ...services.Service import Service


@dataclass
class SQLService(Service):
    
    connection_str : str = field(default=None, metadata={"description": "connection string for the specific SQL database"})
    
    def __post_init__(self):
        super().__post_init__()
        self._conn = None
        self._cursor = None
    
    def _on_start(self):
        self._conn = pyodbc.connect(self.connection_str)
        self._cursor = self._conn.cursor()
        
    def _on_stop(self):
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

