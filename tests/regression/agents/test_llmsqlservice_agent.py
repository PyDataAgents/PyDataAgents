import configparser
import os

from pydag.agents.Agent import Agent
from pydag.services.llm.LLMRestService import LLMRestService
from pydag.services.llm.LLMSQLService import LLMSQLService


def test_000():
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    ag = Agent()
    
    lss = LLMSQLService()
    lss.id = "S1"
    lss.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    lss.model = "gpt-4o"
    lss.model_provider = "OPENAI"
    lss.sql_connection = "sqlite:///" + os.path.dirname(__file__).replace("\\", "/") + "/Chinook.db"
    
    ag.add_service(lss)
    
    lrs = LLMRestService(id="S2", port=10004)
    
    ag.add_service(lrs)
    
    ag.release()