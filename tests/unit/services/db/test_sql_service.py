import os

import pytest
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
    
    sql_service = SQLService(connection_str=connection_str)
    
    sql_service.install()
    sql_service.start()
    
    drivers = sql_service.get_odbc_drivers()
    print("Available ODBC drivers:", drivers)
    
    results = sql_service.fetch(select="COUNT(*) AS count", from_="artist")
    for row in results:
        print(row)