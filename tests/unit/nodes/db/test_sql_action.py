import os
import pytest
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.NodeException import NodeException
from pydag.nodes.db.SQLAction import SQLAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction

def test_sql_select():
    sqlite_file = os.path.dirname(__file__) + os.sep + "Chinook.db"
    connection_str = "DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";"
    query = "SELECT * FROM artist LIMIT 3;"
    sa = SQLAction(
        connection_str=connection_str,
        query=query
    )
    
    sa.install()
    sa.execute()
    
    data = sa.get_buffer().data()
    print(data)
    assert len(data["Name"]) == 3
    
def test_sql_insert():
    sqlite_file = os.path.dirname(__file__) + os.sep + "Chinook.db"
    connection_str = "DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";"
    query1 = "SELECT MAX(ArtistId) AS ID FROM artist;"
    
    sa = SQLAction(
        connection_str=connection_str,
        query=query1
    )
    sa.install()
    sa.execute()
    data = sa.get_buffer().data()
    print(data)
    new_id = data["ID"][0] + 1
    
    sa.uninstall()
    query2 = f"INSERT INTO artist (ArtistId, Name) VALUES ({new_id}, 'Test Artist');"
    sa.query = query2
    sa.install()    
    sa.execute()
    
    sa.uninstall()
    sa.query = query1
    sa.install()
    sa.execute()
    
    data = sa.get_buffer().data()
    print(data)
    
def test_sql_delete():
    sqlite_file = os.path.dirname(__file__) + os.sep + "Chinook.db"
    connection_str = "DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";"
    query1 = "DELETE FROM artist WHERE ArtistId = 1000;"
    
    sa = SQLAction(
        connection_str=connection_str,
        query=query1
    )
    sa.install()
    sa.execute()
    
    query2 = "SELECT MAX(ArtistId) AS ID FROM artist;"
    sa.uninstall()
    sa.query = query2
    sa.install()
    sa.execute()
    
    data = sa.get_buffer().data()
    print(data)
    assert data["ID"][0] < 1000
    
def test_sql_update():
    sqlite_file = os.path.dirname(__file__) + os.sep + "Chinook.db"
    connection_str = "DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";"
    query1 = "UPDATE artist SET Name = 'Updated Artist' WHERE ArtistId = 999;"
    
    sa = SQLAction(
        connection_str=connection_str,
        query=query1
    )
    sa.install()
    sa.execute()
    
    query2 = "SELECT Name FROM artist WHERE ArtistId = 999;"
    sa.uninstall()
    sa.query = query2
    sa.install()
    sa.execute()
    
    data = sa.get_buffer().data()
    print(data)
    assert data["Name"][0] == "Updated Artist"
    
    query3 = "UPDATE artist SET Name = 'Test Artist' WHERE ArtistId = 999;"
    sa.uninstall()
    sa.query = query3
    sa.install()
    sa.execute()
    
    sa.uninstall()
    sa.query = query2
    sa.install()
    sa.execute()
    data = sa.get_buffer().data()
    print(data)
    assert data["Name"][0] == "Test Artist"    
    
def test_faulty_sql():
    sqlite_file = os.path.dirname(__file__) + os.sep + "Chinook.db"
    connection_str = "DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";"
    query = "SELECT * FROM non_existent_table;"
    
    sa = SQLAction(
        connection_str=connection_str,
        query=query
    )
    
    sa.install()
    with pytest.raises(NodeException) as exc_info:
        sa.execute()
    
def testsql_insert_from_buffer():
    sqlite_file = os.path.dirname(__file__) + os.sep + "Chinook.db"
    connection_str = "DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";"
    
    buf = DictBuffer()
    buf.install()
    buf.push({"Name": ["New Artist 3", "New Artist 4"]})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    
    query1 = "INSERT INTO artist (Name) VALUES (?);"
    sa = SQLAction(
        connection_str=connection_str,
        query=query1,
        input_keys=["Name"]
    )
    sa.add_parent(lba)
    sa.install()
    sa.execute()
    
    # Now verify the insert
    query2 = "SELECT Name FROM artist ORDER BY ArtistId DESC LIMIT 2;"
    sa.uninstall()
    sa.query = query2
    sa.install()
    sa.execute()
    data = sa.get_buffer().data()
    print(data)
    assert data["Name"][0] == "New Artist 4"
    assert data["Name"][1] == "New Artist 3"
    
def testsql_insert_from_buffer_multiple_keys():
    sqlite_file = os.path.dirname(__file__) + os.sep + "Chinook.db"
    connection_str = "DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";"
    
    buf = DictBuffer()
    buf.install()
    buf.push({"Name": ["New Artist 3", "New Artist 4"], "ArtistId": [9998, 9999]})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    
    query1 = "INSERT INTO artist (ArtistId, Name) VALUES (?, ?);"
    sa = SQLAction(
        connection_str=connection_str,
        query=query1,
        input_keys=["ArtistId", "Name"]
    )
    sa.add_parent(lba)
    sa.install()
    sa.execute()
    
    # Now verify the insert
    query2 = "SELECT Name FROM artist ORDER BY ArtistId DESC LIMIT 2;"
    sa.uninstall()
    sa.query = query2
    sa.install()
    sa.execute()
    data = sa.get_buffer().data()
    print(data)
    assert data["Name"][0] == "New Artist 4"
    assert data["Name"][1] == "New Artist 3"

def test_sql_update_from_buffer():
    sqlite_file = os.path.dirname(__file__) + os.sep + "Chinook.db"
    connection_str = "DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";"
    
    buf = DictBuffer()
    buf.install()
    buf.push({"Name": ["Another Update"]})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    
    query1 = "UPDATE artist SET Name = ? WHERE ArtistId > 1000;"
    sa = SQLAction(
        connection_str=connection_str,
        query=query1,
        input_keys=["ArtistId", "Name"]
    )
    sa.add_parent(lba)
    sa.install()
    sa.execute()
    
    # Now verify the insert
    query2 = "SELECT Name FROM artist ORDER BY ArtistId DESC LIMIT 1;"
    sa.uninstall()
    sa.query = query2
    sa.install()
    sa.execute()
    data = sa.get_buffer().data()
    print(data)
    assert data["Name"][0] == "Another Update"
    

def test_sql_delete_cleanup():
    sqlite_file = os.path.dirname(__file__) + os.sep + "Chinook.db"
    connection_str = "DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";"
    query1 = "DELETE FROM artist WHERE ArtistId >= 1000;"
    
    sa = SQLAction(
        connection_str=connection_str,
        query=query1
    )
    sa.install()
    sa.execute()
    
    # Now verify the insert
    query2 = "SELECT ArtistId FROM artist ORDER BY ArtistId DESC LIMIT 1;"
    sa.uninstall()
    sa.query = query2
    sa.install()
    sa.execute()
    data = sa.get_buffer().data()
    print(data)
    assert data["ArtistId"][0] == 999    

    