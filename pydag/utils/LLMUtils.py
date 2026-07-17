from typing import Annotated, Any, Callable, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, BaseMessage, HumanMessage
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages

try:
    from langgraph.checkpoint.memory import InMemorySaver
except ImportError:  # pragma: no cover - compatibility with older LangGraph releases
    from langgraph.checkpoint.memory import MemorySaver as InMemorySaver


class MessageHistoryState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    question: str
    instruction: str
    input_context: str
    retrieval_query: str
    use_rag_context: bool
    internet_context: str


def compile_message_history_graph(
    call_model: Callable[[MessageHistoryState, list[AnyMessage]], Any],
):
    """Compile a one-node LangGraph with thread-scoped chat history."""

    def call_model_node(state: MessageHistoryState):
        messages = state.get("messages", [])
        history_messages = messages[:-1] if messages else []
        return {"messages": [_as_ai_message(call_model(state, history_messages))]}

    builder = StateGraph(MessageHistoryState)
    builder.add_node("call_model", call_model_node)
    builder.add_edge(START, "call_model")
    return builder.compile(checkpointer=InMemorySaver())


def build_message_history_input(payload: dict[str, Any]) -> dict[str, Any]:
    graph_input = dict(payload)
    graph_input["messages"] = [HumanMessage(content=str(payload["question"]))]
    return graph_input


def get_message_content(message_or_state: Any) -> str:
    if isinstance(message_or_state, dict) and "messages" in message_or_state:
        message_or_state = message_or_state["messages"][-1]
    if isinstance(message_or_state, str):
        return message_or_state
    return message_or_state.content


def _as_ai_message(message: str | BaseMessage) -> BaseMessage:
    if isinstance(message, BaseMessage):
        return message
    if hasattr(message, "content"):
        return AIMessage(content=str(message.content))
    return AIMessage(content=str(message))
