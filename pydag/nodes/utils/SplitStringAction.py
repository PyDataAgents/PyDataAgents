from dataclasses import dataclass, field
from pathlib import Path
import textwrap

from ..NodeException import NodeException
from ...agents.Agent import Agent
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class SplitStringAction(BufferNode, Action):
    """An `Action` that splits incoming filenames by a delimiter into separate output columns."""

    delimiter: str = field(default="_", metadata={"description": "delimiter used to split the incoming filename into separate fields"})
    parsing_functions: list[str] = field(default_factory=list, metadata={"description": "optional per-output parsing functions to apply after splitting"})

    def __post_init__(self):
        super().__post_init__()
        self._parsing_handlers: list[callable] = []

    def _on_install(self, agent: Agent = None):
        super()._on_install(agent)
        if len(self.parsing_functions) > 0 and len(self.parsing_functions) != len(self.output_keys):
            raise NodeException(f"{self.cname()} requires the same number of parsing_functions as output_keys ({len(self.output_keys)}), got {len(self.parsing_functions)}")
        if len(self.parsing_functions) > 0:
            for pf in self.parsing_functions:
                if pf:
                    namespace = {}
                    source = textwrap.dedent(pf).strip()
                    if not source:
                        self._parsing_handlers.append(None)
                        continue
                    exec(source, namespace)
                    fns = [value for value in namespace.values() if callable(value)]
                    if not fns:
                        raise NodeException(f"No callable parsing function could be extracted from: {pf}")
                    self._parsing_handlers.append(fns[0])
                else:
                    self._parsing_handlers.append(None)

    def _on_execute(self):
        data = self.get_parent_data(by_rows=True)
        row : dict
        for row in data:
            for key, val in row.items():
                filename = str(val)
                filename = Path(filename).stem
                parts = filename.split(self.delimiter)

                if len(parts) != len(self.output_keys):
                    raise NodeException(f"Expected {len(self.output_keys)} parsed filename parts for '{filename}', but got {len(parts)}: {parts}")

                parsed_row = {}
                for i, key in enumerate(self.output_keys):
                    value = parts[i]
                    if len(self._parsing_handlers) > 0:
                        if self._parsing_handlers[i]:
                            value = self._parsing_handlers[i](value)
                    parsed_row[key] = value        
                self.add_data(parsed_row)