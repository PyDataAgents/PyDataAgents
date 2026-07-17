import configparser

import pytest
from langchain_core.messages import AIMessage

from pydag.services.llm.LLMService import LLMService, ModelProvider


class DummyChain:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def invoke(self, payload, config=None):
        self.calls.append({"payload": payload, "config": config})
        return self.response


class DummySearchTool:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def invoke(self, query):
        self.calls.append(query)
        return self.response


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


def test_llmservice_chat_prefetches_internet_context_when_enabled():
    search_tool = DummySearchTool(
        {
            "results": [
                {
                    "title": "Example result",
                    "url": "https://example.test/result",
                    "content": "Fresh context from Tavily.",
                }
            ]
        }
    )
    service = LLMService(use_internet_context=True)
    service._internet_search_tool = search_tool
    service._langchain = DummyChain("ok")

    assert service.chat("What changed today?") == "ok"

    assert search_tool.calls == ["What changed today?"]
    model_question = service._langchain.calls[0]["payload"]["question"]
    assert "Question:\nWhat changed today?" in model_question
    assert "Internet Context:" in model_question
    assert "Example result" in model_question
    assert "Fresh context from Tavily." in model_question


def test_llmservice_chat_skips_internet_context_when_disabled_or_call_disabled():
    for service, kwargs in [
        (LLMService(use_internet_context=False), {}),
        (LLMService(use_internet_context=True), {"use_internet_context": False}),
    ]:
        service._internet_search_tool = DummySearchTool("unused")
        service._langchain = DummyChain("ok")
        assert service.chat("What changed today?", **kwargs) == "ok"
        assert service._internet_search_tool.calls == []
        assert service._langchain.calls[0]["payload"]["question"] == "What changed today?"


# This test performs real internet access through Tavily. It requires a Tavily API key.
# Move it back to regression tests if it becomes flaky or slow.
def test_llmservice_tavily_internet_context_returns_real_web_text():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("TAVILY") or not config.has_option("TAVILY", "TAVILY_API_KEY"):
        pytest.skip("Skipping Tavily internet test: Tavily internet access requires TAVILY_API_KEY in [TAVILY] of config.ini")

    service = LLMService(use_internet_context=True, tavily_api_key=config["TAVILY"]["TAVILY_API_KEY"])
    context = service._get_internet_context_text("OpenAI official website")

    assert context.strip() != ""
    assert "OpenAI" in context


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
