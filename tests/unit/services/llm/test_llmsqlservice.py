import configparser
import os
from langchain_community.utilities import SQLDatabase
import pytest

pytest.importorskip("langgraph")


from pydag.services.llm.LLMSQLService import LLMSQLService


def test_000():
    db = SQLDatabase.from_uri("sqlite:///" + os.path.dirname(__file__).replace("\\", "/") + "/Chinook.db")
    print(db.dialect)
    print(db.get_usable_table_names())
    print(db.get_context())
    print(db.run("SELECT * FROM Artist LIMIT 10;"))
    
def test_001():
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    lss = LLMSQLService()
    lss.id = "S1"
    lss.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    lss.model = "gpt-4o"
    lss.model_provider = "OPENAI"
    lss.sql_connection = "sqlite:///" + os.path.dirname(__file__).replace("\\", "/") + "/Chinook.db"
        
    lss.install()
    lss.start()
    print(lss._write_query({"question": "How many Employees are there?"}))
    
def test_002():
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    lss = LLMSQLService()
    lss.id = "S1"
    lss.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    lss.model = "gpt-4o"
    lss.model_provider = "OPENAI"
    lss.sql_connection = "sqlite:///" + os.path.dirname(__file__).replace("\\", "/") + "/Chinook.db"
    lss.install()
    lss.start()
    print(lss._write_query({"question": "What is the most popular artist based on invoices of customers?"}))

def test_010():    
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    lss = LLMSQLService()
    lss.id = "S1"
    lss.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    lss.model = "gpt-4o"
    lss.model_provider = "OPENAI"
    lss.sql_connection = "sqlite:///" + os.path.dirname(__file__).replace("\\", "/") + "/Chinook.db"
    
    lss.install()
    
    lss.start()
    
    ans = lss.chat("What is the most popular artist based on invoices of customers?")
    print(ans)

@pytest.mark.skip(reason="Requires OLLAMA server running locally")      
def test_011():    
    #config = configparser.ConfigParser()
    #config.read("config.ini")    
    lss = LLMSQLService()
    lss.id = "S1"
    lss.endpoint = "http://localhost:11434"
    lss.model = "sqlcoder:latest"
    lss.model_provider = "OLLAMA"
    lss.sql_connection = "sqlite:///" + os.path.dirname(__file__).replace("\\", "/") + "/Chinook.db"
    
    lss.install()
    
    lss.start()
    
    ans = lss.chat("What is the most popular artist based on invoices of customers?")
    print(ans)
    
    lss.stop()
    
