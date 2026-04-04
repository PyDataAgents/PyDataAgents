from __future__ import annotations
import copy
from dataclasses import dataclass, field
import time


from ..buffers.BufferException import BufferException
from ..agents.AgentConfig import AgentConfig
from .Buffer import Buffer
from ..agents import Agent


@dataclass
class DictBuffer(Buffer):
    """
    Buffer that stores its values in a dictionary column-wise (each key -> list).
    """
    timestamps_enabled : bool = field(default=False, metadata={"description": "Whether timestamps are enabled for this buffer. If the parent buffer has a timestamps column which is named in the same way as this buffer's timestamps_key, those timestamps will be copied over. If set to False and a timestamp column is present in the input data, it will be ignored."})
    timestamps_key  : str = field(default="timestamps", metadata={"description": "Key under which timestamps are exposed."})
    index_enabled : bool = field(default=False, metadata={"description": "Whether an index column is enabled for this buffer. The index column is a simple integer sequence starting from 0 and adds +1 per point. If the parent buffer has an index column which is named in the same way as this buffer's index_key, those indices will be copied over. If set to False and an index column is present in the input data, it will be ignored."})
    index_key : str = field(default="index", metadata={"description": "Key name for index column."})

    def __post_init__(self):
        super().__post_init__()
        self._elements = {}
        self._index = 0
        
    def _on_push(self, elements: list | dict):
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
        # Case: list of dicts (iterate)
        if isinstance(elements, list) and all(isinstance(el, dict) for el in elements):
            for el in elements:
                self._on_push(el)
            return
        elif isinstance(elements, dict):
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
                        if not isinstance(v, (int, float)):
                            raise ValueError(f"Unsupported type for key '{k}': {type(v)}. Only lists and scalars (int, float) are supported.")
                        else:
                            elements[k] = [v] * batch_len

            # Prevent empty batch inserts (e.g., pushing a dict with empty lists)
            # This avoids alignment padding and timestamp/index generation on zero-length pushes.
            if batch_len == 0:
                return
            
            # Normalize user-provided timestamp / index columns based on enabled flags
            if not self.timestamps_enabled and self.timestamps_key in elements:
                del elements[self.timestamps_key]
            if not self.index_enabled and self.index_key in elements:
                del elements[self.index_key]

            if self.timestamps_enabled and self.timestamps_key in elements:
                ts_val = elements[self.timestamps_key]
                if isinstance(ts_val, list):
                    if len(ts_val) != batch_len:
                        raise ValueError(f"Timestamps list length {len(ts_val)} != batch length {batch_len}")
                else:
                    if batch_len > 1:
                        elements[self.timestamps_key] = [ts_val] * batch_len
                    # batch_len == 1 keeps scalar

            if self.index_enabled and self.index_key in elements:
                idx_val = elements[self.index_key]
                if isinstance(idx_val, list):
                    if len(idx_val) != batch_len:
                        raise ValueError(f"Index list length {len(idx_val)} != batch length {batch_len}")
                else:
                    if batch_len > 1:
                        elements[self.index_key] = [idx_val] * batch_len
                    # batch_len == 1 keeps scalar
            # Determine existing non-meta columns; always exclude meta columns from alignment padding.
            meta_keys = {self.timestamps_key, self.index_key}
            excluded = set()
            if not self.timestamps_enabled:
                excluded.add(self.timestamps_key)
            if not self.index_enabled:
                excluded.add(self.index_key)
            # Reject meta-only payloads before any insertion
            non_meta_incoming = [k for k in elements.keys() if k not in meta_keys]
            if len(non_meta_incoming) == 0:
                return
            # existing columns excluding meta keys entirely for alignment purposes
            existing_cols = [c for c in self._elements.keys() if c not in meta_keys]
            current_size = self.size()

            # New incoming columns: pad past rows with None.
            # Always ignore meta columns (timestamps/index) here; they are handled separately below.
            for col in elements.keys():
                if col in meta_keys:  # meta columns handled later
                    continue
                if col in self._elements:  # already present
                    continue
                if current_size > 0:
                    self._elements[col] = [None] * current_size
                else:
                    self._elements[col] = []

            # Existing columns missing in this incoming batch: extend with None placeholders
            for col in existing_cols:
                if col not in elements:
                    if batch_len > 1:
                        self._elements[col].extend([None] * batch_len)
                    else:
                        self._elements[col].append(None)

            # Insert values
            time_now = time.time_ns() # time in nanoseconds
            st = time.perf_counter_ns() # start ns timer
            if time_now <= self._last_timestamp:
                dt =  st - self._last_timer
                if dt == 0:
                    dt = 1  # ensure some positive delta to maintain monotonicity
                time_now = self._last_timestamp + dt
            for k, v in elements.items():
                if k not in self._elements:
                    self._elements[k] = []
                if isinstance(v, list):
                    # List of length batch_len
                    self._elements[k].extend(v)
                else:
                    # Scalar (batch_len == 1 case)
                    self._elements[k].append(v)
            et = time.perf_counter_ns() # end ns timer
            el = et - st # elapsed time in ns for precise timestamp insertion
            #time_then = time.time_ns() # time in nanoseconds

            # Timestamps handling:
            # If timestamps are enabled and user provides them, they were already inserted above.
            # If enabled but not provided: always generate timestamps for the incoming batch
            # (whether the timestamps column exists already or not). This ensures timestamps
            # consistently represent the value columns and avoids None padding.
            if self.timestamps_enabled:
                if self.timestamps_key not in elements:
                    if self.timestamps_key not in self._elements:
                        self._elements[self.timestamps_key] = []
                    # Generate timestamps based on batch size
                    if batch_len == 1:
                        ts_list = [time_now]
                    else:
                        interval = el / batch_len
                        ts_list = [int(time_now + interval * i) for i in range(batch_len)]
                    self._elements[self.timestamps_key].extend(ts_list)

            if self.index_enabled:        
                if self.index_key not in elements:
                    if self.index_key not in self._elements:
                        self._elements[self.index_key] = []                           
                        if batch_len == 1:
                            index_list = [self._index]
                        else:
                            index_list = [self._index + i for i in range(batch_len)]
                            self._index += batch_len
                    else:
                        elin = self._elements[self.index_key]
                        if isinstance(elin, list):
                            if len(elin) == 0:
                                base = self._index
                            else:
                                base = elin[-1] + 1
                                self._index = base
                            index_list = [base + i for i in range(batch_len)]
                        else:
                            if batch_len == 1:
                                base = int(elin) + 1 if elin is not None else self._index
                                self._index = base
                                index_list = [base]
                            else:
                                index_list = [None] * batch_len
                        self._index += batch_len
                    self._elements[self.index_key].extend(index_list)

            # Capacity enforcement
            if self.capacity != AgentConfig.INFINITE_CAPACITY:
                final_size = self.size()
                if final_size > self.capacity:
                    drop = final_size - self.capacity
                    for col, col_data in self._elements.items():
                        del col_data[0:drop]
            
            self._last_timer = time.perf_counter_ns()
            self._last_timestamp = time_now
        else:
            # non dict elements case, force the insertion with a standard key or already present key (but only if only one user-specified key is present)
            if len(self._elements) == 0:
                dic = {AgentConfig.VALUES: elements}
                self._on_push(dic)
            else:
                keys = list(self._elements.keys())
                if self.timestamps_key in keys:
                    keys.remove(self.timestamps_key)
                if self.index_key in keys:
                    keys.remove(self.index_key)
                if len(keys) == 1:
                    dic = {keys[0]: elements}
                    self._on_push(dic)
                else:                
                    raise BufferException("Unsupported elements type for push: " + str(type(elements)) + ". Must be dict or list of dicts or the " + self.cname() + " is only allowed to have 1 user-defined key.")

    def _on_data(self, n=0, persistent=True) -> dict:
        if n > 0:
            if len(self._elements) == 0:
                return {}
            # Adjust n to available
            first_col = next(iter(self._elements.values()))
            if len(first_col) < n:
                n = len(first_col)
            d = {}
            for k, lst in self._elements.items():
                d[k] = lst[0:n]
            if not persistent:
                with self._lock:
                    for k in list(self._elements.keys()):
                        del self._elements[k][0:n]
            return d
        else:
            if len(self._elements) == 0:
                return {}
            d = copy.deepcopy(self._elements)
            if not persistent:
                with self._lock:
                    for k in self._elements.keys():
                        self._elements[k].clear()
            return d
            
    def data_with_meta(self, n = 0, persistent = True) -> dict:        
        d = {}
        d[AgentConfig.DATA] = self.data(n, persistent)
        d[AgentConfig.META] = self.config_options()
        return d

    def size(self) -> int:
        """ returns the size of this `DictBuffer`

        Returns:
            int: number of samples in dict
        """
        # size determined by first non-timestamp column (or timestamps if only column)
        if len(self._elements) == 0:
            return 0
        for k, v in self._elements.items():
            if k != self.timestamps_key:
                return len(v)
        # Fallback: only timestamps present
        return len(next(iter(self._elements.values())))


