import os
import pyodbc
import pytest
from pydag.buffers.DictBuffer import DictBuffer
from pydag.services.MappingType import MappingType
from pydag.services.ThreadType import ThreadType
from pydag.services.db.SQLService import SQLService


@pytest.mark.skip("for this to work, you need to have a local/docker SQL Server instance running")
def test_000():
    
    connection_str = """DRIVER={ODBC Driver 18 for SQL Server};
        SERVER=localhost,1433;
        DATABASE=AdventureWorks2022;
        UID=sa;
        PWD=Admin1234!;
        TrustServerCertificate=yes;"""
    
    sql_service = SQLService(connection_str=connection_str)
    
    sql_service.install()
    sql_service.start()
    
    drivers = sql_service.get_odbc_drivers()
    print("Available ODBC drivers:", drivers)
    
    results = sql_service.fetch(select="name", from_="sys.databases")
    for row in results:
        print(row)
        

def test_010():
    sqlite_file = os.path.dirname(__file__) + os.sep + "Chinook.db"
    connection_str = "DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";"
    
    sql_service = SQLService(connection_str=connection_str, thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.READ.value)
    
    sql_service.install()
    
    drivers = sql_service.get_odbc_drivers()
    print("Available ODBC drivers:", drivers)
    
    results = sql_service.fetch(select="COUNT(*) AS count", from_="artist")
    for row in results:
        print(row)
        

def test_011():
    a = SQLService()
    print(a.config_options())

def test_012():
    sqlite_file = os.path.dirname(__file__) + os.sep + "test1.sqlite"
    conn = pyodbc.connect("DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";")
    cursor = conn.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS benutzer;
        ''')    
    # Änderungen speichern
    conn.commit()    
    # Verbindung schließen
    cursor.close()
    conn.close()
    
def test_013():
    sqlite_file = os.path.dirname(__file__) + os.sep + "test1.sqlite"
    conn = pyodbc.connect("DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS benutzer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER
        )
        ''')    
    # Änderungen speichern
    conn.commit()    
    # Verbindung schließen
    cursor.close()
    conn.close()
    
def test_014():
    sqlite_file = os.path.dirname(__file__) + os.sep + "test1.sqlite"
    conn = pyodbc.connect("DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";")
    cursor = conn.cursor()
    # Beispiel-Daten, die eingefügt werden sollen
    name = "John Doe"
    email = "johndoe@example.com"
    age = 20

    # SQL-Befehl zum Einfügen von Daten
    cursor.execute('''
        INSERT INTO benutzer (name, email, age)
        VALUES (?, ?, ?)
    ''', (name, email, age))

    # Änderungen speichern
    conn.commit()

    # Verbindung schließen
    conn.close()

def test_015():
    sqlite_file = os.path.dirname(__file__) + os.sep + "test1.sqlite"
    conn = pyodbc.connect("DRIVER={SQLite3 ODBC Driver};DATABASE=" + sqlite_file + ";")
    cursor = conn.cursor()
    # Alle Daten aus der Tabelle 'benutzer' auslesen
    cursor.execute('SELECT id, name FROM benutzer')

    # Alle Zeilen holen
    alle_zeilen = cursor.fetchall()
    # Get column names from cursor.description
    columns = [column[0] for column in cursor.description]
    # Convert each row to a dictionary {column_name: value}
    data_with_columns = [dict(zip(columns, row)) for row in alle_zeilen]
    
    # Jede Zeile ausgeben
    for row_dict in data_with_columns:
        print(row_dict )

    # Verbindung schließen
    conn.close()
    

@pytest.mark.skip(reason="for this test to work, you need to have a local/docker SQL Server instance running under localhost:1433")
def test_020():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=localhost,1433;"
        "DATABASE=AdventureWorks2022;"
        "UID=sa;"
        "PWD=Admin1234!;"
        "TrustServerCertificate=yes;"
    )
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sys.databases')

    # Alle Zeilen holen
    alle_zeilen = cursor.fetchall()
    # Get column names from cursor.description
    columns = [column[0] for column in cursor.description]
    # Convert each row to a dictionary {column_name: value}
    data_with_columns = [dict(zip(columns, row)) for row in alle_zeilen]
    
    # Jede Zeile ausgeben
    for row_dict in data_with_columns:
        print(row_dict )

    # Verbindung schließen
    conn.close()


def test_030():
    sqlite_file = os.path.dirname(__file__) + os.sep + "test2.sqlite"    
    connection_str = f"DRIVER={{SQLite3 ODBC Driver}};DATABASE={sqlite_file};"
    print(connection_str)
    addresses = ["""
                 DROP TABLE IF EXISTS benutzer;
                 """]
    sql = SQLService(connection_str=connection_str, addresses=addresses, thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.WRITE.value)    
    sql.install()    
    sql.write_to_sink()    
    sql.uninstall()    

def test_031():
    sqlite_file = os.path.dirname(__file__) + os.sep + "test2.sqlite"    
    connection_str = f"DRIVER={{SQLite3 ODBC Driver}};DATABASE={sqlite_file};"
    print(connection_str)
    addresses = ["""
                 CREATE TABLE IF NOT EXISTS benutzer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    age INTEGER
                )
                 """]    
    sql = SQLService(connection_str=connection_str, addresses=addresses, thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.WRITE.value)
    
    sql.install()        
    sql.write_to_sink()
    sql.uninstall()
    
def test_032():
    sqlite_file = os.path.dirname(__file__) + os.sep + "test2.sqlite"    
    connection_str = f"DRIVER={{SQLite3 ODBC Driver}};DATABASE={sqlite_file};"
    print(connection_str)
    
    buf = DictBuffer()
    buf.install()
    buf.push({"name": "John Doe", "email": "john.doe@aol.com", "age": 20})
    
    addresses = ["INSERT INTO benutzer (name, email, age) VALUES (?, ?, ?)"]
    sql = SQLService(connection_str=connection_str, addresses=addresses, thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.WRITE.value)
    sql.add_buffer(buf)   
    sql.install()    
    sql.write_to_sink()
    sql.uninstall()
    
def test_033():
    sqlite_file = os.path.dirname(__file__) + os.sep + "test2.sqlite"    
    connection_str = f"DRIVER={{SQLite3 ODBC Driver}};DATABASE={sqlite_file};"
    print(connection_str)
    
    addresses = ["INSERT INTO benutzer (name, email, age) VALUES (?, ?, ?)"]
    
    buf = DictBuffer()
    buf.install()
    buf.push({"name": "Paul Allen", "email": "p.allen@gmail.com", "age": 45})
    
    sql = SQLService(connection_str=connection_str, addresses=addresses, thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.WRITE.value)
    sql.add_buffer(buf)
    
    sql.install()
    sql.write_to_sink()
    sql.uninstall()
    
def test_034():
    sqlite_file = os.path.dirname(__file__) + os.sep + "test2.sqlite"    
    connection_str = f"DRIVER={{SQLite3 ODBC Driver}};DATABASE={sqlite_file};"
    print(connection_str)
    addresses = ["SELECT id, name FROM benutzer"]
    
    buf = DictBuffer()
    buf.install()
    
    sql = SQLService(connection_str=connection_str, addresses=addresses, thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.READ.value)
    sql.add_buffer(buf)
    
    sql.install()    
    sql.read_from_source()
    sql.uninstall()
    
    print(buf.data())
    
def test_035():
    sqlite_file = os.path.dirname(__file__) + os.sep + "test2.sqlite"    
    connection_str = f"DRIVER={{SQLite3 ODBC Driver}};DATABASE={sqlite_file};"
    print(connection_str)
    addresses = ["UPDATE benutzer SET name = ?, email = ? WHERE id = 1"]
    
    buf = DictBuffer()
    buf.install()
    buf.push({"name": "Max Mustermann", "email": "m.mustermann@outlook.com"})
    
    sql = SQLService(connection_str=connection_str, addresses=addresses, thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.WRITE.value)
    sql.add_buffer(buf)
    
    sql.install()    
    sql.write_to_sink()
    
    addresses = ["SELECT id, name FROM benutzer"]
    
    buf2 = DictBuffer()
    sql.addresses = addresses
    sql.get_buffers().clear()
    sql.add_buffer(buf2)
    
    buf2.install()       
    sql.read_from_source()
    
    sql.uninstall()
    
    print(buf2.data())
    
    
def test_036():
    sqlite_file = os.path.dirname(__file__) + os.sep + "test2.sqlite"    
    connection_str = f"DRIVER={{SQLite3 ODBC Driver}};DATABASE={sqlite_file};"
    print(connection_str)
    addresses = ["DELETE FROM benutzer WHERE id = 1"]
    sql = SQLService(connection_str=connection_str, addresses=addresses, thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.WRITE.value)
    
    sql.install()        
    sql.write_to_sink()
    
    sql.uninstall()
    