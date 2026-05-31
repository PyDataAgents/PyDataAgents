
import configparser

import pytest

pytest.importorskip("langgraph")

from pydag.agents.Agent import Agent
from pydag.services.llm.LLMService import LLMService
from pydag.services.llm.RAGService import RAGService
from pydag.services.llm.LLMRestAPI import LLMRestAPI

def test_010():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("OPENAI") or not config.has_option("OPENAI", "OPENAI_API_KEY"):
        pytest.skip("Skipping RAG regression test: missing OPENAI_API_KEY in [OPENAI] of config.ini")
    
    ag = Agent()
    
    rs = RAGService()
    rs.id = "RAG1"
    rs.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    rs.model = "gpt-4o"
    rs.model_provider = "OPENAI"
    rs.retain_messages = True
        
    ag.add_service(rs)
    
    ls = LLMService()
    ls.id = "LLM1"
    ls.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    ls.model = "gpt-4o-mini"
    ls.model_provider = "OPENAI"
    ls.retain_messages = True
    
    ag.add_service(ls)
    
    ag.create_api(no_default_routers=True)  # Create API without default routers to avoid conflicts with other tests
    ag.add_api(LLMRestAPI.get_api_router(ag))
    
    ag.release()
    
def test_020():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("OPENAI") or not config.has_option("OPENAI", "OPENAI_API_KEY"):
        pytest.skip("Skipping RAG regression test: missing OPENAI_API_KEY in [OPENAI] of config.ini")
    
    g = Agent()
    
    rs = RAGService()
    rs.id = "RAG1"
    rs.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    rs.model = "gpt-4o"
    rs.model_provider = "OPENAI"
    rs.retain_messages = True
        
    g.add_service(rs)
          
    g.create_api(no_default_routers=True)  # Create API without default routers to avoid conflicts with other tests
    g.add_api(LLMRestAPI.get_api_router(g))
    
    g.release()
