
import configparser

import pytest

pytest.importorskip("langgraph")

from pydag.agents.Agent import Agent
from pydag.services.llm.LLMRestService import LLMRestService
from pydag.services.llm.LLMService import LLMService
from pydag.services.llm.RAGService import RAGService


def test_010():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    g = Agent()
    
    rs = RAGService()
    rs.id = "RAG1"
    rs.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    rs.model = "gpt-4o"
    rs.model_provider = "OPENAI"
    rs.retain_messages = True
        
    g.add_service(rs)
    
    ls = LLMService()
    ls.id = "LLM1"
    ls.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    ls.model = "gpt-4o-mini"
    ls.model_provider = "OPENAI"
    ls.retain_messages = True
    
    g.add_service(ls)
    
    lrs = LLMRestService()
    lrs.id = "LLM-REST1"
    lrs.port = 8001
    
    g.add_service(lrs)
    
    g.release()
    
def test_020():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    g = Agent()
    
    rs = RAGService()
    rs.id = "RAG1"
    rs.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    rs.model = "gpt-4o"
    rs.model_provider = "OPENAI"
    rs.retain_messages = True
        
    g.add_service(rs)
        
    lrs = LLMRestService()
    lrs.id = "LLM-REST1"
    lrs.port = 8001
    
    g.add_service(lrs)
    
    g.release()
