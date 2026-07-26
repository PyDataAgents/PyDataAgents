import base64
import configparser

import pytest
from langchain_core.messages import AIMessage

from pydag.services.ServiceException import ServiceException
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


class RecordingChatModel:
    def __init__(self, response="ok"):
        self.response = response
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        return AIMessage(content=self.response)


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


@pytest.mark.parametrize("provider", [ModelProvider.OPENAI.value, ModelProvider.AZURE.value])
def test_llmservice_file_context_dispatches_openai_compatible_providers(provider):
    service = LLMService(model_provider=provider)
    service._llm = RecordingChatModel()

    assert service.chat("Describe the file", context_files="https://example.test/file.pdf") == "ok"

    messages = service._llm.calls[0]
    content = messages[-1].content
    assert content[0]["type"] == "text"
    assert "Describe the file" in content[0]["text"]
    assert content[1] == {
        "type": "file",
        "url": "https://example.test/file.pdf",
        "filename": "file.pdf",
        "mime_type": "application/pdf",
    }


def test_llmservice_file_context_builds_multiple_remote_blocks():
    service = LLMService(model_provider=ModelProvider.OPENAI.value)
    service._llm = RecordingChatModel()

    service.chat(
        "Describe these files",
        context_files=[
            "https://example.test/image.png",
            "https://example.test/file.pdf",
        ],
    )

    content = service._llm.calls[0][-1].content
    assert content[1] == {"type": "image_url", "image_url": {"url": "https://example.test/image.png"}}
    assert content[2]["type"] == "file"
    assert content[2]["url"] == "https://example.test/file.pdf"
    assert content[2]["filename"] == "file.pdf"


def test_llmservice_file_context_builds_local_path_and_file_url_blocks(tmp_path, monkeypatch):
    local_pdf = tmp_path / "local.pdf"
    local_pdf.write_bytes(b"%PDF-test")
    local_image = tmp_path / "local.jpg"
    local_image.write_bytes(b"jpg-test")
    monkeypatch.chdir(tmp_path)
    service = LLMService(model_provider=ModelProvider.OPENAI.value)
    service._llm = RecordingChatModel()

    service.chat("Describe local files", context_files=["local.pdf", local_pdf.as_uri(), "local.jpg"])

    content = service._llm.calls[0][-1].content
    expected_base64 = base64.b64encode(b"%PDF-test").decode("utf-8")
    expected_image_base64 = base64.b64encode(b"jpg-test").decode("utf-8")
    assert content[1]["type"] == "file"
    assert content[1]["base64"] == expected_base64
    assert content[1]["filename"] == "local.pdf"
    assert content[1]["mime_type"] == "application/pdf"
    assert content[2]["base64"] == expected_base64
    assert content[3] == {
        "type": "image_url",
        "image_url": {"url": "data:image/jpeg;base64," + expected_image_base64},
    }


def test_llmservice_file_context_builds_data_uri_base64_and_raw_bytes_blocks():
    service = LLMService(model_provider=ModelProvider.OPENAI.value)
    service._llm = RecordingChatModel()
    image_payload = base64.b64encode(b"image-bytes").decode("utf-8")
    file_payload = base64.b64encode(b"file-bytes").decode("utf-8")

    service.chat(
        "Describe inline files",
        context_files=[
            "data:image/png;base64," + image_payload,
            file_payload,
            b"raw-bytes",
        ],
    )

    content = service._llm.calls[0][-1].content
    assert content[1] == {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image_payload}}
    assert content[2] == {
        "type": "file",
        "base64": file_payload,
        "filename": "context_file_2",
        "mime_type": "application/octet-stream",
    }
    assert content[3] == {
        "type": "file",
        "base64": base64.b64encode(b"raw-bytes").decode("utf-8"),
        "filename": "context_file_3",
        "mime_type": "application/octet-stream",
    }


def test_llmservice_empty_context_files_uses_existing_text_chain():
    service = LLMService()
    service._langchain = DummyChain("ok")

    assert service.chat("Q", context_files=[]) == "ok"

    assert len(service._langchain.calls) == 1
    assert service._langchain.calls[0]["payload"]["question"] == "Q"


def test_llmservice_ollama_file_context_warns_and_does_not_normalize(monkeypatch):
    service = LLMService(model_provider=ModelProvider.OLLAMA.value)
    service._langchain = DummyChain("ok")

    def fail_if_called(_context_files):
        raise AssertionError("Ollama placeholder must not normalize or process files")

    monkeypatch.setattr(service, "_normalize_context_files", fail_if_called)

    with pytest.warns(RuntimeWarning, match="supported only for OPENAI and AZURE"):
        assert service.chat("Q", context_files="C:/missing/file.pdf") == "ok"

    assert len(service._langchain.calls) == 1
    assert service._langchain.calls[0]["payload"]["question"] == "Q"


@pytest.mark.parametrize(
    "context_files",
    [
        {"url": "https://example.test/file.pdf"},
        "ftp://example.test/file.pdf",
        "",
        "https://",
        "not-base64@@",
    ],
)
def test_llmservice_rejects_invalid_context_file_inputs(context_files):
    service = LLMService(model_provider=ModelProvider.OPENAI.value)
    service._llm = RecordingChatModel()

    with pytest.raises(ServiceException):
        service.chat("Q", context_files=context_files)


def test_llmservice_rejects_missing_local_context_file(tmp_path):
    service = LLMService(model_provider=ModelProvider.OPENAI.value)
    service._llm = RecordingChatModel()

    with pytest.raises(ServiceException):
        service.chat("Q", context_files=str(tmp_path / "missing.pdf"))


def test_llmservice_rejects_files_for_unsupported_provider():
    service = LLMService(model_provider=ModelProvider.LANGDOCK.value)
    service._llm = RecordingChatModel()

    with pytest.raises(ServiceException):
        service.chat("Q", context_files="https://example.test/file.pdf")


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
