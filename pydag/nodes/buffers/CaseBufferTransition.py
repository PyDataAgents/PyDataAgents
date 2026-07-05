from dataclasses import dataclass, field
import operator
import re
from typing import Any, Callable, ClassVar

from loguru import logger

from ...buffers.Comparator import Comparator
from ..BufferNode import BufferNode
from ..NodeException import NodeException
from ..Transition import Transition


@dataclass
class CaseBufferTransition(BufferNode, Transition):
    """
    A buffer-aware transition that checks parent buffer data and forwards matching
    payload data to its own buffer.
    """

    case_key: str = field(default=None, metadata={"description": "key from parent buffer data used for case evaluation"})
    comparator: str = field(default=Comparator.EQUAL.value, metadata={"description": "comparison operator to use for case evaluation"})
    value: Any = field(default=None, metadata={"description": "target value used by the comparator"})
    check_n: int = field(default=1, metadata={"description": "number of parent rows used for checking the case"})
    payload_n: int = field(default=0, metadata={"description": "number of parent rows moved to this transition buffer after a successful check"})
    payload_keys: list[str] | list[int] | str = field(default_factory=list, metadata={"description": "keys, indices, or selector pattern moved to this transition buffer after a successful check. If empty, all parent keys are moved"})
    default: bool = field(default=False, metadata={"description": "if True, the transition passes without evaluating case_key/comparator/value"})

    REGEX = "REGEX"
    COMPARATOR_ALIASES: ClassVar[dict[str, str]] = {
        "==": Comparator.EQUAL.value,
        "!=": Comparator.NOT_EQUAL.value,
        ">": Comparator.GREATER.value,
        "<": Comparator.LESS.value,
        ">=": Comparator.EQUAL_OR_GREATER.value,
        "<=": Comparator.EQUAL_OR_LESS.value,
    }
    BINARY_COMPARATORS: ClassVar[dict[str, Callable[[Any, Any], bool]]] = {
        Comparator.EQUAL.value: operator.eq,
        Comparator.NOT_EQUAL.value: operator.ne,
        Comparator.GREATER.value: operator.gt,
        Comparator.LESS.value: operator.lt,
        Comparator.EQUAL_OR_GREATER.value: operator.ge,
        Comparator.EQUAL_OR_LESS.value: operator.le,
    }

    def _on_install(self, agent=None):
        super()._on_install(agent)
        BufferNode._validate_keys(self.payload_keys)
        if self.check_n < 0:
            raise NodeException("check_n must be greater than or equal to 0")
        if self.payload_n < 0:
            raise NodeException("payload_n must be greater than or equal to 0")
        if not self.default:
            if self.case_key is None or str(self.case_key).strip() == "":
                raise NodeException("case_key must be configured unless default is True")
            if not self._is_supported_comparator(self.comparator):
                raise NodeException(f"unsupported comparator: {self.comparator}")

    def _on_check(self) -> bool:
        if not self._parent_buffers_have_data():
            return False

        if not self.default and not self._case_matches():
            return False

        if self.payload_keys:
            validation_data = self._read_parent_data(
                n=self.payload_n,
                persistent=True,
                input_keys=self.payload_keys,
                ignore_empty_parents=True,
            )
            if len(validation_data) == 0:
                if not self._parent_buffers_have_data():
                    logger.debug(f"No parent data available for {self.name()}")
                    return False
                raise NodeException("None of the specified input_keys were found in the parent buffers data")

        payload = self._read_parent_data(
            n=self.payload_n,
            persistent=False,
            input_keys=self.payload_keys,
            ignore_empty_parents=True,
        )
        if len(payload) == 0:
            return False

        self.add_data(payload)
        return True

    def _case_matches(self) -> bool:
        data = self._read_parent_data(
            n=self.check_n,
            persistent=True,
            input_keys=[self.case_key],
            ignore_empty_parents=True,
        )
        if len(data) == 0:
            if not self._parent_buffers_have_data():
                logger.debug(f"No parent data available for {self.name()}")
                return False
            if self._parent_buffers_contain_key(self.case_key):
                logger.debug(f"No parent data available for case_key '{self.case_key}' in {self.name()}")
                return False
            raise NodeException(f"case_key '{self.case_key}' was not found in parent buffer data")
        if self.case_key not in data:
            raise NodeException(f"case_key '{self.case_key}' was not found in parent buffer data")

        values = data[self.case_key]
        if not isinstance(values, list):
            values = [values]

        for item in values:
            if self._compare(item):
                return True
        return False

    def _read_parent_data(
        self,
        n: int,
        persistent: bool,
        input_keys: list[str] | list[int] | str,
        ignore_empty_parents: bool,
    ) -> dict:
        original_n = self.n
        original_persistent = self.persistent
        original_input_keys = self.input_keys
        original_ignore_empty_parents = self.ignore_empty_parents
        try:
            self.n = n
            self.persistent = persistent
            self.input_keys = input_keys
            self.ignore_empty_parents = ignore_empty_parents
            return self.get_parent_data()
        finally:
            self.n = original_n
            self.persistent = original_persistent
            self.input_keys = original_input_keys
            self.ignore_empty_parents = original_ignore_empty_parents

    def _parent_buffers_have_data(self) -> bool:
        return any(parent.get_buffer().size() > 0 for parent in self._buffer_parents())

    def _parent_buffers_contain_key(self, key: str) -> bool:
        return any(key in parent.get_buffer().data(n=1, persistent=True) for parent in self._buffer_parents())

    def _buffer_parents(self) -> list[BufferNode]:
        if len(self._parents) == 0:
            self.get_parent_data()

        parents = [parent for parent in self._parents if isinstance(parent, BufferNode)]
        if len(parents) == 0:
            self.get_parent_data()

        for parent in parents:
            if parent.get_buffer() is None:
                raise NodeException(f"Buffer not initialized in parent {parent.id}")
        return parents

    def _compare(self, data: Any) -> bool:
        comparator = self._normalized_comparator()
        if comparator in self.BINARY_COMPARATORS:
            return self.BINARY_COMPARATORS[comparator](data, self.value)
        if comparator == Comparator.LIKE.value:
            return self._contains(data, self.value)
        if comparator == Comparator.NOT_LIKE.value:
            return not self._contains(data, self.value)
        if comparator == Comparator.NOT_NULL.value:
            return data is not None
        if comparator == self.REGEX:
            return isinstance(data, str) and re.search(str(self.value), data) is not None
        raise NodeException(f"unsupported comparator: {self.comparator}")

    @staticmethod
    def _contains(data: Any, value: Any) -> bool:
        if data is None:
            return False
        if isinstance(data, str):
            return str(value) in data
        try:
            return value in data
        except TypeError:
            return False

    @classmethod
    def _is_supported_comparator(cls, comparator: str) -> bool:
        normalized = cls.COMPARATOR_ALIASES.get(comparator, comparator)
        return normalized in {item.value for item in Comparator} or normalized == cls.REGEX

    def _normalized_comparator(self) -> str:
        return self.COMPARATOR_ALIASES.get(self.comparator, self.comparator)
