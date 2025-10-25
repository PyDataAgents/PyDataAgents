import os
import pyodbc
from pydag.adapters.db.SQLAdapter import SQLAdapter


def test_000():
    a = SQLAdapter()
    
def test_010():
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
    
def test_011():
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
    
def test_012():
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
    
    
def test_020():
    """
    for this test to work, you need to have a local/docker SQL Server instance running under localhost:1433
    """
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