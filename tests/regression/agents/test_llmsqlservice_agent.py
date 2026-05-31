import configparser
import os
import pytest

from pydag.agents.Agent import Agent
from pydag.services.llm.LLMRestAPI import LLMRestAPI
from pydag.services.llm.LLMSQLService import LLMSQLService


def test_000():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("OPENAI") or not config.has_option("OPENAI", "OPENAI_API_KEY"):
        pytest.skip("Skipping LLMSQLService agent regression test: missing OPENAI_API_KEY in [OPENAI] of config.ini")
    
    ag = Agent(port=10004)
    
    lss = LLMSQLService()
    lss.id = "S1"
    lss.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    lss.model = "gpt-4o"
    lss.model_provider = "OPENAI"
    lss.sql_connection = "sqlite:///" + os.path.dirname(__file__).replace("\\", "/") + "/Chinook.db"
    
    ag.add_service(lss)
        
    ag.create_api(no_default_routers=True)  # Create API without default routers to avoid conflicts with other tests
    ag.add_api(LLMRestAPI.get_api_router(ag))
            
    ag.release()
