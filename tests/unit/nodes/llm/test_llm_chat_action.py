import json
import sys
import types

import pytest

# Fallback for environments where graphviz is not installed.
if "graphviz" not in sys.modules:
    graphviz_stub = types.ModuleType("graphviz")

    class _DummyDigraph:
        def __init__(self, *args, **kwargs):
            return

        def node(self, *args, **kwargs):
            return

        def edge(self, *args, **kwargs):
            return

        def render(self, *args, **kwargs):
            return ""

    graphviz_stub.Digraph = _DummyDigraph
    sys.modules["graphviz"] = graphviz_stub

from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.NodeException import NodeException
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.llm.LLMChatAction import LLMChatAction
from pydag.services.ServiceException import ServiceException
import pydag.services.llm.LLMService as llm_service_module
from pydag.services.llm.LLMService import LLMService
from pydag.services.llm.RAGService import RAGService
import pydag.utils.ModelUtils as model_utils_module


class RecordingRAGService(RAGService):
    def __post_init__(self):
        super().__post_init__()
        self.calls = []
        self.next_answer = "ok"

    def chat(
        self,
        question: str,
        instruction: str | None = None,
        input_context: str | dict | list | None = None,
        retrieval_query: str | None = None,
        use_rag_context: bool = True,
        session_id: str = "DEFAULT_SESSION",
    ) -> str:
        self.calls.append(
            {
                "question": question,
                "instruction": instruction,
                "input_context": input_context,
                "retrieval_query": retrieval_query,
                "use_rag_context": use_rag_context,
                "session_id": session_id,
            }
        )
        return self.next_answer


def _link_parent_with_row(row: dict):
    parent_buf = DictBuffer(id="PARENT_BUF")
    parent_buf.install()
    parent_buf.push(row)

    lba = LinkBufferAction()
    lba.set_buffer(parent_buf)
    lba.install()
    return lba


def _new_service() -> RecordingRAGService:
    return RecordingRAGService(id="RAG1", model_provider="OLLAMA", model="dummy")


def test_install_enforces_rag_service_only():
    """Ensure install fails when the referenced service is not a RAGService instance."""
    action = LLMChatAction(question_value="hello")
    action.set_service(LLMService(id="LLM1"))

    with pytest.raises(NodeException):
        action.install()


def test_execute_resolves_literals_for_all_runtime_arguments():
    """Ensure key-or-literal resolution supports literal question/instruction/retrieval_query/input_context."""
    service = _new_service()
    service.next_answer = "literal-answer"

    action = LLMChatAction(
        question_value="literal question",
        instruction_value="literal instruction",
        retrieval_query_value="literal retrieval",
        input_context_value={"template": {"k": ""}},
        use_rag_context=True,
    )
    action.set_service(service)
    action.install()
    action.execute()

    output = action.get_buffer().data()
    assert output["question"] == ["literal question"]
    assert output["answer"] == ["literal-answer"]
    assert len(service.calls) == 1
    assert service.calls[0]["question"] == "literal question"
    assert service.calls[0]["instruction"] == "literal instruction"
    assert service.calls[0]["retrieval_query"] == "literal retrieval"
    assert service.calls[0]["input_context"] == {"template": {"k": ""}}
    assert service.calls[0]["use_rag_context"] is True


def test_execute_raises_on_key_and_value_conflict():
    """Ensure the action fails fast when both *_key and *_value are configured for the same argument."""
    service = _new_service()
    action = LLMChatAction(question_key="question", question_value="literal question")
    action.set_service(service)
    action.install()

    with pytest.raises(NodeException):
        action.execute()


def test_execute_raises_on_input_context_key_and_value_conflict():
    """Ensure input_context cannot be configured with both input_context_keys and input_context_value."""
    service = _new_service()
    action = LLMChatAction(
        question_value="q",
        input_context_keys=["ctx"],
        input_context_value={"ctx": "v"},
    )
    action.set_service(service)
    action.install()

    with pytest.raises(NodeException):
        action.execute()


def test_execute_raises_on_missing_configured_parent_key():
    """Ensure missing configured parent keys raise NodeException."""
    service = _new_service()
    action = LLMChatAction(question_key="question")
    action.set_service(service)
    action.add_parent(_link_parent_with_row({"other": "value"}))
    action.install()

    with pytest.raises(NodeException):
        action.execute()


def test_execute_raises_on_template_placeholder_mismatch():
    """Ensure legacy template mode fails if input_keys and placeholders are not aligned."""
    service = _new_service()
    action = LLMChatAction(input_keys=["a", "b"], template="Only one placeholder: {}")
    action.set_service(service)
    action.add_parent(_link_parent_with_row({"a": "x", "b": "y"}))
    action.install()

    with pytest.raises(NodeException):
        action.execute()


def test_mode_chat_only():
    """Mode 1: Chat-Only using RAGService with retrieval disabled and only a question."""
    service = _new_service()
    service.next_answer = "chat-only-answer"

    action = LLMChatAction(
        question_value="What is 1+1?",
        use_rag_context=False,
    )
    action.set_service(service)
    action.install()
    action.execute()

    output = action.get_buffer().data()
    assert output["question"] == ["What is 1+1?"]
    assert output["answer"] == ["chat-only-answer"]
    assert service.calls[0]["retrieval_query"] == "What is 1+1?"
    assert service.calls[0]["use_rag_context"] is False


def test_mode_chat_with_rag_context():
    """Mode 2: Chat-with-RAG-context using question from parent and retrieval enabled."""
    service = _new_service()
    service.next_answer = "rag-answer"

    action = LLMChatAction(question_key="question", use_rag_context=True)
    action.set_service(service)
    action.add_parent(_link_parent_with_row({"question": "Use KB only"}))
    action.install()
    action.execute()

    output = action.get_buffer().data()
    assert output["question"] == ["Use KB only"]
    assert output["answer"] == ["rag-answer"]
    assert service.calls[0]["question"] == "Use KB only"
    assert service.calls[0]["retrieval_query"] == "Use KB only"
    assert service.calls[0]["input_context"] is None
    assert service.calls[0]["use_rag_context"] is True


def test_mode_chat_with_local_context_only():
    """Mode 3: Chat-with-local-context using parent context while retrieval is disabled."""
    service = _new_service()
    service.next_answer = "local-context-answer"

    action = LLMChatAction(
        question_key="question",
        input_context_keys=["context"],
        use_rag_context=False,
    )
    action.set_service(service)
    action.add_parent(
        _link_parent_with_row(
            {
                "question": "Summarize local context",
                "context": {"a": 1, "b": 2},
            }
        )
    )
    action.install()
    action.execute()

    assert service.calls[0]["question"] == "Summarize local context"
    assert service.calls[0]["input_context"] == {"context": {"a": 1, "b": 2}}
    assert service.calls[0]["use_rag_context"] is False


def test_mode_full_augment():
    """Mode 4: Full-mode-augment with question + instruction + local context + RAG context."""
    service = _new_service()
    service.next_answer = '{"kasse":"AOK"}'

    action = LLMChatAction(
        question_key="question",
        instruction_key="instruction",
        retrieval_query_key="retrieval_query",
        input_context_keys=["fields", "metadata"],
        input_context_mode="augment",
        use_rag_context=True,
    )
    action.set_service(service)
    action.add_parent(
        _link_parent_with_row(
            {
                "question": "Fill fields",
                "instruction": "Return field mapping only",
                "retrieval_query": "insurance form rules",
                "fields": [[{"field_id": "kasse", "current_value": ""}]],
                "metadata": {"pages": 1},
            }
        )
    )
    action.install()
    action.execute()

    output = action.get_buffer().data()
    assert output["answer"] == ['{"kasse":"AOK"}']
    assert service.calls[0]["question"] == "Fill fields"
    assert service.calls[0]["instruction"] == "Return field mapping only"
    assert service.calls[0]["retrieval_query"] == "insurance form rules"
    assert service.calls[0]["input_context"] == {
        "fields": [{"field_id": "kasse", "current_value": ""}],
        "metadata": {"pages": 1},
    }
    assert service.calls[0]["use_rag_context"] is True


def test_use_rag_context_defaults_to_false_when_not_configured():
    """Ensure use_rag_context defaults to False if not explicitly configured."""
    service = _new_service()
    service.next_answer = "answer"

    action = LLMChatAction(question_value="Q")
    action.set_service(service)
    action.install()
    action.execute()

    assert len(service.calls) == 1
    assert service.calls[0]["use_rag_context"] is False


def test_mode_full_template_fill_success():
    """Mode 5: Full-mode-template_fill validates and accepts matching answer structure."""
    service = _new_service()
    service.next_answer = '{"fields":[{"field_id":"kasse","current_value":"AOK"}]}'

    action = LLMChatAction(
        question_key="question",
        instruction_key="instruction",
        input_context_keys=["fields"],
        input_context_mode="template_fill",
    )
    action.set_service(service)
    action.add_parent(
        _link_parent_with_row(
            {
                "question": "Fill the template",
                "instruction": "Return same structure only",
                "fields": [[{"field_id": "kasse", "current_value": ""}]],
            }
        )
    )
    action.install()
    action.execute()

    output = action.get_buffer().data()
    parsed = json.loads(output["answer"][0])
    assert parsed == {"fields": [{"field_id": "kasse", "current_value": "AOK"}]}


def test_mode_full_template_fill_structure_mismatch_fails_fast():
    """Mode 5: Full-mode-template_fill fails fast when answer structure mismatches input_context."""
    service = _new_service()
    service.next_answer = '{"fields":[{"field_id":"kasse"}]}'

    action = LLMChatAction(
        question_key="question",
        instruction_key="instruction",
        input_context_keys=["fields"],
        input_context_mode="template_fill",
    )
    action.set_service(service)
    action.add_parent(
        _link_parent_with_row(
            {
                "question": "Fill the template",
                "instruction": "Return same structure only",
                "fields": [[{"field_id": "kasse", "current_value": ""}]],
            }
        )
    )
    action.install()
    with pytest.raises(NodeException):
        action.execute()


def test_template_fill_requires_input_context():
    """Ensure template_fill mode fails if input_context is missing."""
    service = _new_service()
    service.next_answer = '{"a":1}'

    action = LLMChatAction(
        question_value="Fill template",
        input_context_mode="template_fill",
    )
    action.set_service(service)
    action.install()

    with pytest.raises(NodeException):
        action.execute()


def test_template_fill_invalid_json_answer_fails_fast():
    """Ensure template_fill mode fails when the model answer is not valid JSON."""
    service = _new_service()
    service.next_answer = "not-json"

    action = LLMChatAction(
        question_value="Fill template",
        input_context_value={"k": ""},
        input_context_mode="template_fill",
    )
    action.set_service(service)
    action.install()

    with pytest.raises(NodeException):
        action.execute()


def test_pass_through_keys_are_copied_to_output():
    """Ensure configured pass_through keys are copied unchanged to the output row."""
    service = _new_service()
    service.next_answer = "answer"

    action = LLMChatAction(
        question_key="question",
        pass_through_keys=["filepath"],
    )
    action.set_service(service)
    action.add_parent(
        _link_parent_with_row(
            {
                "question": "Q",
                "filepath": "C:/tmp/a.pdf",
            }
        )
    )
    action.install()
    action.execute()

    output = action.get_buffer().data()
    assert output["question"] == ["Q"]
    assert output["answer"] == ["answer"]
    assert output["filepath"] == ["C:/tmp/a.pdf"]


def test_pass_through_missing_key_raises():
    """Ensure missing configured pass_through keys fail fast with NodeException."""
    service = _new_service()
    service.next_answer = "answer"

    action = LLMChatAction(
        question_key="question",
        pass_through_keys=["filepath"],
    )
    action.set_service(service)
    action.add_parent(_link_parent_with_row({"question": "Q"}))
    action.install()

    with pytest.raises(NodeException):
        action.execute()


class _FakeOllamaClient:
    def __init__(self, model_names=None, fail_on_list: bool = False, fail_on_pull: bool = False):
        self._model_names = set(model_names or [])
        self._fail_on_list = fail_on_list
        self._fail_on_pull = fail_on_pull
        self.pull_calls = []

    def list(self):
        if self._fail_on_list:
            raise RuntimeError("list failed")
        return types.SimpleNamespace(models=[types.SimpleNamespace(model=name) for name in sorted(self._model_names)])

    def pull(self, model, stream=False, insecure=False):
        if self._fail_on_pull:
            raise RuntimeError("pull failed")
        self.pull_calls.append({"model": model, "stream": stream, "insecure": insecure})
        self._model_names.add(model)
        return types.SimpleNamespace(status="success")


def test_modelutils_ensure_skips_pull_when_model_already_available(monkeypatch):
    fake_client = _FakeOllamaClient(model_names=["llama3.1"])
    monkeypatch.setattr(
        model_utils_module.ModelUtils,
        "get_ollama_client",
        staticmethod(lambda _endpoint: fake_client),
    )

    model_utils_module.ModelUtils.ensure_ollama_model_available("llama3.1", "http://localhost:11434")

    assert fake_client.pull_calls == []


def test_modelutils_ensure_accepts_latest_tag_for_untagged_model(monkeypatch):
    fake_client = _FakeOllamaClient(model_names=["llama3.1:latest"])
    monkeypatch.setattr(
        model_utils_module.ModelUtils,
        "get_ollama_client",
        staticmethod(lambda _endpoint: fake_client),
    )

    model_utils_module.ModelUtils.ensure_ollama_model_available("llama3.1", "http://localhost:11434")

    assert fake_client.pull_calls == []


def test_modelutils_ensure_pulls_missing_model(monkeypatch):
    fake_client = _FakeOllamaClient(model_names=[])
    monkeypatch.setattr(
        model_utils_module.ModelUtils,
        "get_ollama_client",
        staticmethod(lambda _endpoint: fake_client),
    )

    model_utils_module.ModelUtils.ensure_ollama_model_available("llama3.1", "http://localhost:11434")

    assert len(fake_client.pull_calls) == 1
    assert fake_client.pull_calls[0]["model"] == "llama3.1"
    assert fake_client.pull_calls[0]["stream"] is False


def test_modelutils_ensure_raises_actionable_error_on_pull_failure(monkeypatch):
    fake_client = _FakeOllamaClient(model_names=[], fail_on_pull=True)
    monkeypatch.setattr(
        model_utils_module.ModelUtils,
        "get_ollama_client",
        staticmethod(lambda _endpoint: fake_client),
    )

    with pytest.raises(RuntimeError) as exc_info:
        model_utils_module.ModelUtils.ensure_ollama_model_available("llama3.1", "http://localhost:11434")

    message = str(exc_info.value)
    assert "ollama pull llama3.1" in message
    assert "http://localhost:11434" in message


def test_modelutils_ensure_raises_actionable_error_on_list_failure(monkeypatch):
    fake_client = _FakeOllamaClient(model_names=[], fail_on_list=True)
    monkeypatch.setattr(
        model_utils_module.ModelUtils,
        "get_ollama_client",
        staticmethod(lambda _endpoint: fake_client),
    )

    with pytest.raises(RuntimeError) as exc_info:
        model_utils_module.ModelUtils.ensure_ollama_model_available("llama3.1", "http://localhost:11434")

    assert "ollama pull llama3.1" in str(exc_info.value)


def test_llmservice_ollama_branch_calls_modelutils_before_ollama_llm(monkeypatch):
    call_order = []

    def _fake_ensure(model, endpoint):
        call_order.append(("ensure", model, endpoint))

    class _FakeOllamaLLM:
        def __init__(self, model, base_url=None):
            call_order.append(("create", model, base_url))

    monkeypatch.setattr(
        llm_service_module.ModelUtils,
        "ensure_ollama_model_available",
        staticmethod(_fake_ensure),
    )
    monkeypatch.setattr(llm_service_module, "OllamaLLM", _FakeOllamaLLM)

    service = LLMService(model_provider="OLLAMA", model="llama3.1", endpoint="http://localhost:11434")
    service._create_llm()

    assert call_order[0] == ("ensure", "llama3.1", "http://localhost:11434")
    assert call_order[1] == ("create", "llama3.1", "http://localhost:11434")


def test_llmservice_openai_branch_does_not_call_modelutils(monkeypatch):
    ensure_calls = []

    def _fake_ensure(_model, _endpoint):
        ensure_calls.append(True)

    class _FakeChatOpenAI:
        def __init__(self, model_name, openai_api_key=None, temperature=1):
            self.model_name = model_name
            self.openai_api_key = openai_api_key
            self.temperature = temperature

    monkeypatch.setattr(
        llm_service_module.ModelUtils,
        "ensure_ollama_model_available",
        staticmethod(_fake_ensure),
    )
    monkeypatch.setattr(llm_service_module, "ChatOpenAI", _FakeChatOpenAI)

    service = LLMService(model_provider="OPENAI", model="gpt-4.1-mini", api_key="fake-key")
    service._create_llm()

    assert ensure_calls == []


def test_llmservice_wraps_modelutils_failures_as_serviceexception(monkeypatch):
    def _failing_ensure(model, endpoint):
        raise RuntimeError("simulated ensure failure for " + model + "@" + str(endpoint))

    monkeypatch.setattr(
        llm_service_module.ModelUtils,
        "ensure_ollama_model_available",
        staticmethod(_failing_ensure),
    )

    service = LLMService(model_provider="OLLAMA", model="llama3.1", endpoint="http://localhost:11434")

    with pytest.raises(ServiceException) as exc_info:
        service._create_llm()

    message = str(exc_info.value)
    assert "Failed to ensure Ollama model 'llama3.1'" in message
    assert "http://localhost:11434" in message


def test_ragservice_create_llm_and_chain_calls_inherited_create_llm(monkeypatch):
    create_llm_calls = []
    import pydag.services.llm.RAGService as rag_module

    class _Pipe:
        def __or__(self, _other):
            return _Pipe()

        def __ror__(self, _other):
            return _Pipe()

    def _fake_create_llm(self):
        create_llm_calls.append(self.cname())
        self._llm = _Pipe()

    monkeypatch.setattr(LLMService, "_create_llm", _fake_create_llm)
    monkeypatch.setattr(
        rag_module,
        "ChatPromptTemplate",
        types.SimpleNamespace(from_messages=lambda _messages: _Pipe()),
    )
    monkeypatch.setattr(rag_module, "RunnableMap", lambda _mapping: _Pipe())

    service = RAGService(model_provider="OLLAMA", model="llama3.1", retain_messages=False)
    service._retriever = types.SimpleNamespace(get_relevant_documents=lambda _query: [])

    service._create_llm_and_chain()

    assert len(create_llm_calls) == 1
