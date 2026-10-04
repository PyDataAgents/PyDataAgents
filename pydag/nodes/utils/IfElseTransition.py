import json
import operator
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar

from ..BufferNode import BufferNode
from ..Node import Node
from ..NodeException import NodeException
from ..Transition import Transition


@dataclass
class IfElseTransition(BufferNode, Transition):
    """Route JSON parent data to the first (true) or second (false) child.

    A JSONPath query selects values from the column-oriented parent data.
    ``match_mode`` combines comparisons using any/all; no matches is false.
    ``check()`` returns True for either branch, allowing SFCService to advance.
    ``get_next_children()`` returns the selected branch after checking.
    Requires jsonpath-ng (available in the iiot extra).
    """

    json_path: str = field(default="$", metadata={"description": "JSONPath query over parent data, e.g. $.temperature[-1]"})
    condition: str = field(default="equals", metadata={"description": "equals, not_equals, greater_than, greater_or_equal, less_than, less_or_equal, contains, exists, is_null, or is_not_null"})
    value: Any = field(default=None, metadata={"description": "JSON value to compare with each query match"})
    match_mode: str = field(default="any", metadata={"description": "Combine matched conditions using any or all; no matches is always false"})

    COMPARISONS: ClassVar[dict[str, Callable]] = {
        "equals": operator.eq,
        "not_equals": operator.ne,
        "greater_than": operator.gt,
        "greater_or_equal": operator.ge,
        "less_than": operator.lt,
        "less_or_equal": operator.le,
        "contains": operator.contains,
    }

    def __post_init__(self):
        super().__post_init__()
        self._query = None
        self._selected_child: Node | None = None

    def _validate_children(self):
        children = self.get_children()
        if len(children) != 2 or children[0].id == children[1].id:
            raise NodeException("IfElseTransition requires exactly two distinct children: true, then false")

    def _on_install(self, agent=None):
        self._selected_child = None
        self._validate_children()
        if self.condition not in {*self.COMPARISONS, "exists", "is_null", "is_not_null"}:
            raise NodeException(f"Unsupported condition: {self.condition}")
        if self.match_mode not in ("any", "all"):
            raise NodeException("match_mode must be any or all")
        if not isinstance(self.json_path, str) or not self.json_path.strip():
            raise NodeException("json_path must be a non-empty JSONPath query")
        if self.n < 0:
            raise NodeException("n must be greater than or equal to 0")
        try:
            from jsonpath_ng import parse
        except ImportError as exc:
            raise NodeException("IfElseTransition requires jsonpath-ng; install pydag[iiot]") from exc
        try:
            self._query = parse(self.json_path)
        except Exception as exc:
            raise NodeException("Invalid json_path query") from exc
        super()._on_install(agent)

    def _on_uninstall(self, agent=None):
        self._query = None
        self._selected_child = None
        super()._on_uninstall(agent)

    def _on_check(self) -> bool:
        self._selected_child = None
        self._validate_children()
        data = self.get_parent_data()
        try:
            document = json.loads(json.dumps(data, allow_nan=False))
            matches = self._query.find(document)
            results = [self._matches(match.value) for match in matches]
            result = bool(results) and (any(results) if self.match_mode == "any" else all(results))
        except (TypeError, ValueError, KeyError, IndexError, OverflowError) as exc:
            raise NodeException("Cannot evaluate JSON condition: check data types and query") from exc
        self.get_buffer().clear()
        self.add_data(data)
        self._selected_child = self.get_children()[0 if result else 1]
        return True

    def _matches(self, actual: Any) -> bool:
        if self.condition == "exists":
            return True
        if self.condition == "is_null":
            return actual is None
        if self.condition == "is_not_null":
            return actual is not None
        return self.COMPARISONS[self.condition](actual, self.value)

    def get_next_children(self) -> list[Node]:
        return [] if self._selected_child is None else [self._selected_child]
