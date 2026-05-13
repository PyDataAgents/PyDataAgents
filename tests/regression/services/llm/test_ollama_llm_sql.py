import os

from pydag.services.llm.LLMSQLService import LLMSQLService


def test_011():    
    #config = configparser.ConfigParser()
    #config.read("config.ini")
    
    sql_connection = "sqlite:///" + os.path.dirname(__file__).replace("\\", "/") + "/Chinook.db"
    lss = LLMSQLService(id = "S1",
                        endpoint = "http://localhost:11434",
                        model = "sqlcoder:latest",
                        model_provider = "OLLAMA",
                        sql_connection = sql_connection
                        )
    
    lss.install()
    
    lss.start()
    
    ans = lss.chat("What is the most popular artist based on invoices of customers?")
    print(ans)
    
    lss.stop()