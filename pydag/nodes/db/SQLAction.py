from dataclasses import dataclass, field
import pyodbc
from sqlalchemy import table, values
from torch import where

from ...nodes.BufferNode import BufferNode
from ...nodes.NodeException import NodeException
from ...agents.Agent import Agent
from ...nodes.Action import Action


@dataclass
class SQLAction(BufferNode, Action):
    """`Action` node to perform SQL operations using the pyodbc library.
    """
    
    connection_str : str = field(default=None, metadata={"description": "connection string for the specific SQL database"})    
    query : str = field(default=None, metadata={"description": "SQL query to execute. If `input_keys` are defined, the query is treated as a parameterized query and values are taken from the buffers."})
    
    def __post_init__(self):
        super().__post_init__()
        self._conn = None
        self._cursor = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._conn = pyodbc.connect(self.connection_str)
        self._cursor = self._conn.cursor()
        
    def _on_execute(self):
        data = self.get_parent_data()
        # check for query type
        if self.query.strip().lower().startswith("select"):
            self._cursor.execute(self.query)
        elif self.query.strip().lower().startswith("insert"):
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = self.query
            if "(COLUMNS)" in query and "(VALUES)" in query:
                query = query.replace("(COLUMNS)", f"({columns})")
                query = query.replace("(VALUES)", f"({placeholders})")
                self._cursor.execute(query, list(data.values()))
            else:
                self._cursor.execute(query)
        elif self.query.strip().lower().startswith("update"):
            if "(SET)" in self.query:
                set_clause = ', '.join([f"{col} = ?" for col in data.keys()])            
                query = self.query
                query = query.replace("(SET)", set_clause)
                self._cursor.execute(query, tuple(data.values()))
            else:
                self._cursor.execute(self.query)
        elif self.query.strip().lower().startswith("delete"):
            self._cursor.execute(self.query)
        else:
            self._cursor.execute(self.query)
        
        self._conn.commit()
        results = self._cursor.fetchall()
        columns = [column[0] for column in self._cursor.description]
        data_with_columns = [dict(zip(columns, row)) for row in results]
        self.add_data(data_with_columns)
