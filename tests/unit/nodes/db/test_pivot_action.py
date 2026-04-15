import os

from pydag.nodes.db.PivotAction import PivotAction
from pydag.nodes.db.SQLAction import SQLAction


def test_010():
    sqlite_file = os.path.dirname(__file__) + os.sep + "Chinook.db"
    connection_str = "DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";"
    query = "SELECT * FROM Track;"
    
    sa = SQLAction(
        connection_str=connection_str,
        query=query
    )
    
    sa.install()
    sa.execute()
    
    pa = PivotAction(index="Composer", values="TrackId", aggfunc="count")
    pa.add_parent(sa)
    pa.install()
    
    pa.execute()
    
    print(pa.get_buffer().data())