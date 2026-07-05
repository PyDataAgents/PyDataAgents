from dataclasses import dataclass, field
import json
import re
from typing import Any

from pydag.utils.DataUtils import DataUtils

from ...nodes.NodeException import NodeException
from ...agents.Agent import Agent
from ...nodes.Action import Action
from ...nodes.BufferNode import BufferNode
from ...nodes.ServiceNode import ServiceNode
from ...services.llm.RAGService import RAGService


@dataclass
class LLMChatAction(BufferNode, ServiceNode, Action):
    """`Action` to chat with a `RAGService` and store the response in its `Buffer`.

    Usage modes:
    1. Chat-Only: (default) `RAGService` with `use_rag_context=False`, only `question`.
    2. Chat-with-RAG-context: `RAGService` with `question`, retrieval enabled.
    3. Chat-with-local-context: `RAGService` with `question` + `input_context`, `use_rag_context=False`.
    4. Full-mode-augment: `question` + `input_context` + retrieval enabled, no strict structure enforcement.
    5. Full-mode-template_fill: same as full augment plus strict structure validation.
    """

    template: str = field(
        default=None,
        metadata={
            "description": """
            Legacy question template fallback when question_key/question_value are not configured.
            For example: 'How much costs the article number {}?' or
            'Summarize the following text: {0}. And answer the following question: {1}'.
            """,
        },
    )

    question_key: str = field(
        default=None,
        metadata={
            "description": "Key from which to receive the data for the final task/question the model must answer. This is what the generated answer should respond to. ",
        },
    )
    question_value: str = field(
        default=None,
        metadata={
            "description": "Fixed value for the final task/question the model must answer. This is what the generated answer should respond to.",
        },
    )
    instruction_key: str = field(
        default=None,
        metadata={
            "description": "Key from which to receive the Rules on how to answer (format, style, constraints, priorities).",
        },
    )
    instruction_value: str = field(
        default=None,
        metadata={
            "description": "Fixed value for the Rules on how to answer (format, style, constraints, priorities).",
        },
    )
    retrieval_query_key: str = field(
        default=None,
        metadata={
            "description": "Key from which to receive the The query used only for document retrieval from the vector store. ",
        },
    )
    retrieval_query_value: str = field(
        default=None,
        metadata={
            "description": "Fixed value for the query used only for document retrieval from the vector store. ",
        },
    )
    input_context_keys: list[str] = field(
        default_factory=list,
        metadata={
            "description": "Key from which to receive the Additional runtime context passed directly from parent buffers (not retrieved from vector DB).",
        },
    )
    input_context_value: str | dict | list | None = field(
        default=None,
        metadata={
            "description": "Fixed value for the Additional runtime context passed directly from parent buffers (not retrieved from vector DB). if input_context_keys is not configured, this value is used as the input context for all rows.",
        },
    )

    input_context_mode: str = field(
        default="augment",
        metadata={"description": "Either 'augment' or 'template_fill'. 'augment' mode simply appends the input_context to the question and feeds it to the model as one prompt. 'template_fill' mode treats the input_context as a template for the expected answer structure and enforces that the model's answer adheres to this structure by validating that all keys in the input_context are present in the model's answer and that there are no extra keys in the model's answer that are not present in the input_context. This is useful to ensure that the model's answer can be reliably parsed and processed downstream, but it also requires that the input_context is carefully crafted to match the expected answer format."},
    )
    use_rag_context: bool = field(
        default=False,
        metadata={"description": "Set to False to disable vector retrieval for this action."},
    )
    pass_through_keys: list[str] = field(
        default_factory=list,
        metadata={"description": "Row keys that should be copied unchanged to the output row."},
    )
    output_keys: list[str] = field(default_factory=lambda: ["question", "answer"])

    def _on_install(self, agent: Agent = None):
        BufferNode._on_install(self, agent)
        ServiceNode._on_install(self, agent)
        BufferNode._validate_keys(self.input_context_keys)
        BufferNode._validate_keys(self.pass_through_keys)
        if not isinstance(self._service, RAGService):
            raise NodeException("referenced service is not an instance of " + RAGService.cname())
        if len(self.output_keys) < 2:
            raise NodeException(self.cname() + " requires at least 2 output_keys")
        if self.input_context_mode not in {"augment", "template_fill"}:
            raise NodeException("input_context_mode must be either 'augment' or 'template_fill'")

    def _on_execute(self):
        self._validate_key_value_conflicts()
        if self._uses_legacy_template_question():
            self._validate_template_alignment()

        data = data = self.get_parent_data() if len(self._parents) > 0 else {}
        rows = DataUtils.dict_to_list(data) if data else []
        if rows is None:
            rows = []

        if len(rows) == 0:
            if self._has_static_row_input():
                rows = [{}]
            elif self._requires_parent_rows():
                raise NodeException("No parent data available for key-based input resolution")
            else:
                return

        question_output_key = self.output_keys[0]
        answer_output_key = self.output_keys[1]

        for row in rows:
            question = self._resolve_question(row)
            instruction = self._resolve_instruction(row)
            input_context = self._resolve_input_context(row)
            retrieval_query = self._resolve_retrieval_query(row, question)

            answer = self._service.chat(
                question=question,
                instruction=instruction,
                input_context=input_context,
                retrieval_query=retrieval_query,
                use_rag_context=self.use_rag_context,
            )
            normalized_answer = self._normalize_answer_for_mode(answer, input_context)

            result = {
                question_output_key: question,
                answer_output_key: normalized_answer,
            }
            for key in self.pass_through_keys:
                if key not in row:
                    raise NodeException("missing configured pass_through key '" + key + "' in row data")
                result[key] = row[key]

            self.add_data(result)

    def _validate_key_value_conflicts(self):
        pairs = [
            ("question", self.question_key, self.question_value),
            ("instruction", self.instruction_key, self.instruction_value),
            ("retrieval_query", self.retrieval_query_key, self.retrieval_query_value),
            ("input_context", None if len(self.input_context_keys) == 0 else "<keys>", self.input_context_value),
        ]
        for name, key, value in pairs:
            if key is not None and value is not None:
                raise NodeException("configure either " + name + "_key or " + name + "_value, not both")

    def _has_static_row_input(self) -> bool:
        return any(
            value is not None
            for value in [
                self.question_value,
                self.instruction_value,
                self.retrieval_query_value,
                self.input_context_value,
            ]
        )

    def _requires_parent_rows(self) -> bool:
        return any(
            [
                self.question_key is not None,
                self.instruction_key is not None,
                self.retrieval_query_key is not None,
                len(self.input_context_keys) > 0,
                len(self.pass_through_keys) > 0,
                self._uses_legacy_template_question(),
            ]
        )

    def _uses_legacy_template_question(self) -> bool:
        return self.question_key is None and self.question_value is None and self.template is not None

    def _validate_template_alignment(self):
        empty_brackets = self.template.count("{}")
        number_brackets = len(set(re.findall(r"\{\d+\}", self.template)))
        if len(self.input_keys) == empty_brackets or len(self.input_keys) == number_brackets:
            return
        raise NodeException(
            f"number of input_keys({len(self.input_keys)}) and placeholders ({self.template.count('{}')}) in template do not match"
        )

    def _resolve_key_or_value(self, row: dict, key: str | None, value: Any, name: str) -> Any:
        if key is not None:
            if key in row:
                return row[key]
            return self._resolve_nested_key(row, key, name)
        return value

    def _resolve_nested_key(self, row: dict, key: str, name: str) -> Any:
        current: Any = row
        for part in key.split("."):
            if isinstance(current, dict):
                if part not in current:
                    raise NodeException("missing configured key '" + key + "' for " + name)
                current = current[part]
                continue

            if isinstance(current, (list, tuple)):
                try:
                    idx = int(part)
                except Exception as exc:
                    raise NodeException("missing configured key '" + key + "' for " + name) from exc
                if idx < 0 or idx >= len(current):
                    raise NodeException("missing configured key '" + key + "' for " + name)
                current = current[idx]
                continue

            raise NodeException("missing configured key '" + key + "' for " + name)
        return current

    def _resolve_question(self, row: dict) -> str:
        resolved = self._resolve_key_or_value(row, self.question_key, self.question_value, "question")
        if resolved is not None:
            return self._to_prompt_text(resolved)

        if self.template is not None:
            return self.template.format(*row.values())
        return " ".join([str(x) for x in row.values()])

    def _resolve_instruction(self, row: dict) -> str:
        resolved = self._resolve_key_or_value(row, self.instruction_key, self.instruction_value, "instruction")
        if resolved is None:
            return ""
        return self._to_prompt_text(resolved)

    def _resolve_retrieval_query(self, row: dict, question: str) -> str:
        resolved = self._resolve_key_or_value(
            row,
            self.retrieval_query_key,
            self.retrieval_query_value,
            "retrieval_query",
        )
        if resolved is None:
            return question
        return self._to_prompt_text(resolved)

    def _resolve_input_context(self, row: dict) -> str | dict | list | None:
        if len(self.input_context_keys) > 0:
            missing_keys = [key for key in self.input_context_keys if key not in row]
            if len(missing_keys) > 0:
                raise NodeException("missing configured key(s) for input_context: " + ", ".join(missing_keys))
            return {key: row[key] for key in self.input_context_keys}
        return self.input_context_value

    def _to_prompt_text(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, ensure_ascii=True)
        except Exception:
            return str(value)

    def _normalize_answer_for_mode(self, answer: Any, input_context: str | dict | list | None) -> Any:
        if self.input_context_mode == "augment":
            return answer

        template_obj = self._normalize_template_input_context(input_context)
        answer_obj = self._parse_json_payload(answer)
        if not self._has_same_structure(template_obj, answer_obj):
            raise NodeException("template_fill structure mismatch between input_context and answer payload")
        return json.dumps(answer_obj, ensure_ascii=True)

    def _normalize_template_input_context(self, input_context: str | dict | list | None) -> dict | list:
        if input_context is None:
            raise NodeException("template_fill mode requires input_context")
        if isinstance(input_context, (dict, list)):
            return input_context
        if isinstance(input_context, str):
            parsed = self._parse_json_payload(input_context)
            if isinstance(parsed, (dict, list)):
                return parsed
        raise NodeException("template_fill mode requires input_context to be dict/list or JSON string")

    def _parse_json_payload(self, payload: Any) -> Any:
        if isinstance(payload, (dict, list)):
            return payload
        if not isinstance(payload, str):
            raise NodeException("template_fill mode requires answer payload to be JSON serializable text")

        clean = payload.strip()
        if clean.startswith("```"):
            lines = clean.splitlines()
            if len(lines) >= 2:
                lines = lines[1:]
                if len(lines) > 0 and lines[-1].strip().startswith("```"):
                    lines = lines[:-1]
                clean = "\n".join(lines).strip()

        try:
            return json.loads(clean)
        except Exception:
            pass

        object_start = clean.find("{")
        object_end = clean.rfind("}")
        if object_start >= 0 and object_end > object_start:
            try:
                return json.loads(clean[object_start : object_end + 1])
            except Exception:
                pass

        list_start = clean.find("[")
        list_end = clean.rfind("]")
        if list_start >= 0 and list_end > list_start:
            try:
                return json.loads(clean[list_start : list_end + 1])
            except Exception:
                pass

        raise NodeException("template_fill mode requires valid JSON in answer payload")

    def _has_same_structure(self, expected: Any, actual: Any) -> bool:
        if isinstance(expected, dict):
            if not isinstance(actual, dict):
                return False
            if set(expected.keys()) != set(actual.keys()):
                return False
            for key in expected.keys():
                if not self._has_same_structure(expected[key], actual[key]):
                    return False
            return True

        if isinstance(expected, list):
            if not isinstance(actual, list):
                return False
            if len(expected) != len(actual):
                return False
            for idx in range(len(expected)):
                if not self._has_same_structure(expected[idx], actual[idx]):
                    return False
            return True

        return True
