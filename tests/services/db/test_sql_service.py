from pydag.services.db.SQLService import SQLService


def test_000():
    """
    for this to work, you need to have a local/docker SQL Server instance running with the following parameters:
    """
    
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