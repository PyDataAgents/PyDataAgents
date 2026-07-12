import configparser

import pytest

from pydag.services.llm.LLMService import LLMService, ModelProvider


def test_openapi_llm():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("OPENAI") or not config.has_option("OPENAI", "OPENAI_API_KEY"):
        pytest.skip("Skipping LLMService test: missing OPENAI_API_KEY in [OPENAI] of config.ini")
    
    lss = LLMService()
    lss.id = "S1"
    lss.api_key = config["OPENAI"]["OPENAI_API_KEY"]
    lss.model = "gpt-4o"
    lss.model_provider = ModelProvider.OPENAI.value
        
    lss.install()
    lss.start()
    
    ans = lss.chat("What is the capital of Germany")
    assert "Berlin" in ans

def test_langdock_llm():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("LANGDOCK") or not config.has_option("LANGDOCK", "LANGDOCK_API_KEY"):
        pytest.skip("Skipping LLMService test: missing LANGDOCK_API_KEY in [LANGDOCK] of config.ini")
    
    lss = LLMService()
    lss.id = "S1"
    lss.api_key = config["LANGDOCK"]["LANGDOCK_API_KEY"]
    lss.model = "gpt-4o"
    lss.model_provider = ModelProvider.LANGDOCK.value
    lss.endpoint = config["LANGDOCK"]["LANGDOCK_ENDPOINT"]
        
    lss.install()
    lss.start()
    
    ans = lss.chat("What is the capital of Germany")
    assert "Berlin" in ans

@pytest.mark.skip()
def test_ollama_llm():
    pass