from __future__ import annotations
import copy
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Any

from ..agents.AgentConfig import AgentConfig
from .Buffer import Buffer
from ..agents import Agent

import time
import datetime

@dataclass
class DictBuffer(Buffer):
    """
    Buffer that stores its values in a dictionary column-wise (each key -> list).
    """
    timestamps_enabled : bool = field(default=False, metadata={"description": "Whether timestamps are enabled for this buffer."})
    timestamps_key  : str = field(default="timestamps", metadata={"description": "Key under which timestamps are exposed."})
    timestamps_format : str = field(default="unix", metadata={"description": "Format: 'unix' (seconds float) or 'iso' (ISO 8601 strings)."})
        
    def __post_init__(self):
        super().__post_init__()
        self.elements : Dict[str, List[Any]] = {}
        self.lock = threading.RLock()

    def install(self, agent : Agent = None):
        super().install(agent)
        if self.initial_values is not None:
            self.elements = self.initial_values
        
    def uninstall(self, agent : Agent = None):
        super().uninstall(agent)
        self.elements = {}        

    def push(self, elements: list | dict):
        """
        Accepts:
          - dict: a batch insert; values can be scalars or lists. Mixed scalars + lists:
              * If any list present, scalars are broadcast to that list length.
          - list[dict]: sequence of dicts; pushes each individually.
        Behavior:
          - Ensures all columns stay length-aligned (excluding the timestamps column).
          - Adds per-element timestamps if enabled.
          - Capacity enforced once after insertion.
        """
        with self.lock:
            # Case: list of dicts (iterate)
            if isinstance(elements, list) and all(isinstance(el, dict) for el in elements):
                for el in elements:
                    self.push(el)
                return

            if not isinstance(elements, dict):
                return  # Unsupported type

            # Prevent user from injecting timestamps column
            if self.timestamps_key in elements:
                del elements[self.timestamps_key]

            # Determine batch length (rows being added)
            list_lengths = [len(v) for v in elements.values() if isinstance(v, list)]
            if list_lengths:
                first_len = list_lengths[0]
                if any(l != first_len for l in list_lengths[1:]):
                    raise ValueError(f"Inconsistent list lengths in batch insert: {list_lengths}")
                batch_len = first_len
            else:
                batch_len = 1  # scalar-only insert

            # Broadcast scalars if any list present
            if batch_len > 1:
                for k, v in list(elements.items()):
                    if not isinstance(v, list):
                        elements[k] = [v] * batch_len

            existing_cols = [c for c in self.elements.keys() if c != self.timestamps_key]
            current_size = self.size()

            # New incoming columns: pad past rows with None
            for col in elements.keys():
                if col not in existing_cols:
                    if current_size > 0:
                        self.elements[col] = [None] * current_size
                    else:
                        self.elements[col] = []

            # Missing columns this batch: create None placeholders
            for col in existing_cols:
                if col not in elements:
                    # Must match batch_len; broadcast for consistency
                    if batch_len > 1:
                        elements[col] = [None] * batch_len
                    else:
                        elements[col] = None  # single row

            # Insert values
            for k, v in elements.items():
                if k not in self.elements:
                    self.elements[k] = []
                if isinstance(v, list):
                    # List of length batch_len
                    self.elements[k].extend(v)
                else:
                    # Scalar (batch_len == 1 case)
                    self.elements[k].append(v)

            # Timestamps (per element) if enabled
            if self.timestamps_enabled:
                if self.timestamps_key not in self.elements:
                    self.elements[self.timestamps_key] = []
                if self.timestamps_format == "unix":
                    if batch_len == 1:
                        ts_list = [time.time()]
                    else:
                        # Per-element distinct timestamps
                        ts_list = [time.time() for _ in range(batch_len)]
                elif self.timestamps_format == "iso":
                    if batch_len == 1:
                        ts_list = [datetime.datetime.now().isoformat()]
                    else:
                        ts_list = [datetime.datetime.now().isoformat() for _ in range(batch_len)]
                else:
                    ts_list = [time.time() for _ in range(batch_len)]
                self.elements[self.timestamps_key].extend(ts_list)

            # Capacity enforcement
            if self.capacity != AgentConfig.INFINITE_CAPACITY:
                final_size = self.size()
                if final_size > self.capacity:
                    drop = final_size - self.capacity
                    for col, col_data in self.elements.items():
                        del col_data[0:drop]

    def data(self, n=0, persistent=True) -> dict:
        if n > 0:
            if len(self.elements) == 0:
                return None
            # Adjust n to available
            first_col = next(iter(self.elements.values()))
            if len(first_col) < n:
                n = len(first_col)
            d = {}
            for k, lst in self.elements.items():
                d[k] = lst[0:n]
            if not persistent:
                for k in list(self.elements.keys()):
                    del self.elements[k][0:n]
            return d
        else:
            if len(self.elements) == 0:
                return None
            d = copy.deepcopy(self.elements)
            if not persistent:
                for k in self.elements.keys():
                    self.elements[k].clear()
            return d
            
    def data_with_meta(self, n = 0, persistent = True) -> dict:        
        d = {}
        d[AgentConfig.DATA] = self.data(n, persistent)
        d[AgentConfig.META] = self.config_options()
        return d

    def size(self) -> int:
        # size determined by first non-timestamp column (or timestamps if only column)
        if not self.elements:
            return 0
        for k, v in self.elements.items():
            if k != self.timestamps_key:
                return len(v)
        # Fallback: only timestamps present
        return len(next(iter(self.elements.values())))
        
    def clear(self):
        self.elements.clear()
        
    def to_html(self) -> str:
        DEFAULT_CELL_STYLE : str = "border: 1px solid black; border-collapse: collapse; padding: 5px"
        data = self.data()
        if not data:
            return "<table></table>"
        # Exclude timestamps from tabular rows if present
        display_cols = [k for k in data.keys() if k != self.timestamps_key]
        if not display_cols:
            display_cols = list(data.keys())
        rows = zip(*[data[c] for c in display_cols])
        html = "<table border='1' style='" + DEFAULT_CELL_STYLE + "'>\n"
        html += "  <tr>" + "".join(f"<th>{col}</th>" for col in display_cols) + "</tr>\n"
        for row in rows:
            html += "  <tr>" + "".join(f"<td>{val}</td>" for val in row) + "</tr>\n"
        html += "</table>"
        return html


