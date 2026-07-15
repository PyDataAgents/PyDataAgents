import configparser

import pytest
from langchain_core.messages import AIMessage

from pydag.services.llm.LLMService import LLMService, ModelProvider


def test_retained_messages_use_langgraph_thread_history(monkeypatch):
    prompts = []

    def fake_create_llm(self):
        def echo_model(prompt_value):
            prompts.append(prompt_value)
            return AIMessage(content="echo-" + str(len(prompts)))

        self._llm = echo_model

    monkeypatch.setattr(LLMService, "_create_llm", fake_create_llm)

    service = LLMService(retain_messages=True)
    service._on_start()

    assert service.chat("Q1") == "echo-1"
    assert service.chat("Q2") == "echo-2"

    second_prompt_messages = prompts[1].to_messages()
    assert [message.content for message in second_prompt_messages] == [
        "Q1",
        "echo-1",
        "Q2",
    ]


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
