import os

from pydag.nodes.db.SQLAction import SQLAction

def test_sql_select():
    sqlite_file = os.path.dirname(__file__) + os.sep + "Chinook.db"
    connection_str = "DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";"
    query = "SELECT Name FROM artist LIMIT 3;"
    sa = SQLAction(
        connection_str=connection_str,
        query=query
    )
    
    sa.install()
    sa.execute()
    
    data = sa.get_buffer().data()
    print(data)
    assert len(data["Name"]) == 3
    