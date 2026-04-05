from dataclasses import dataclass, field
import pyodbc

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
        if self.query is None:
            raise NodeException(f"Query cannot be None for {SQLAction.__name__}")
        
    def _on_execute(self):
        try:
            # check for query type
            if self.query.strip().lower().startswith("select"):
                # SELECT
                self._cursor.execute(self.query)            
                self._conn.commit()
                results = self._cursor.fetchall()
                columns = [column[0] for column in self._cursor.description]
                data_with_columns = [dict(zip(columns, row)) for row in results]
                self.add_data(data_with_columns)
            elif self.query.strip().lower().startswith("insert"):
                # INSERT
                if "?" in self.query:
                    data = self.get_parent_data()                    
                    if self.by_rows:
                        row : dict = next(iter(data))
                        if len(row.keys()) == self.query.count("?"):
                            tuple_data = tuple(list(row.values()) for row in data)
                            self._cursor.executemany(self.query, tuple_data)
                        else:
                            raise NodeException(f"Number of input keys must match the number of parameters in the query {self.query} for {SQLAction.__name__}")
                    else:
                        if len(data.keys()) == self.query.count("?"):
                            tuple_data = list(zip(*data.values()))
                            self._cursor.executemany(self.query, tuple_data)
                        else:
                            raise NodeException(f"Number of input keys must match the number of parameters in the query {self.query} for {SQLAction.__name__}")                    
                else:
                    self._cursor.execute(self.query)
                self._conn.commit()
            elif self.query.strip().lower().startswith("update"):
                # UPDATE
                if "?" in self.query:
                    data = self.get_parent_data()
                    if self.by_rows:
                        row : dict = next(iter(data))
                        if len(row.keys()) == self.query.count("?"):
                            tuple_data = tuple(list(row.values()) for row in data)
                            self._cursor.executemany(self.query, tuple_data)
                        else:
                            raise NodeException(f"Number of input keys must match the number of parameters in the query {self.query} for {SQLAction.__name__}")
                    else:
                        if len(data.keys()) == self.query.count("?"):
                            self._cursor.executemany(self.query, tuple(data.values()))
                        else:
                            raise NodeException(f"Number of input keys must match the number of parameters in the query {self.query} for {SQLAction.__name__}")
                else:
                    self._cursor.execute(self.query)
                self._conn.commit()
            else:
                # DELETE, CREATE, ...
                self._cursor.execute(self.query)
                self._conn.commit()
        except pyodbc.Error as e:
            raise NodeException(f"Error executing SQL query: {e}") from e
            
            
        
