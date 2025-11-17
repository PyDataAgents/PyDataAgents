from dataclasses import dataclass, field
from pydag.agents.AgentConfig import AgentConfig
from ...agents.Agent import Agent
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class CopyDataAction(BufferNode, Action):
    
    forward : bool = field(default=False, metadata={"description": "specifies whether the parent buffer pointer is moved forward if persistent is True. This prevents, that the same data is copied multiple times and we do not have to delete data from the parents buffer to receive newer data."})
    
    """ `Action` that makes a copy of the `Buffer` found in the first `BufferNode` found amongst this `Node`s parents and adds it to a buffer with infinite capacity.
        If this `Node`'s parents contain more than one `BufferNode`, only the first is respected.
    """
    
    def __post_init__(self):
        super().__post_init__()
        self.parent_ref : BufferNode = None
        self.pointer : int = 0  # pointer to keep track of current position in parent buffer
    
    def install(self, agent : Agent = None):
        BufferNode.install(self, agent)
        # check parents for first BufferNode and reference the parent
        for parent in self.parents:
            if isinstance(parent, BufferNode):
                self.parent_ref = parent                    
                break

    def execute(self):
        if not self.persistent:
            raise RuntimeError("CopyDataAction requires persistent=True.")

        parent_full = self.parent_ref.buffer.data(persistent=True)
        if not parent_full:
            return
        prev_full = self.buffer.data(persistent=True) or {}

        list_cols = [k for k, v in parent_full.items() if isinstance(v, list)]
        if not list_cols:
            if not prev_full:
                self.buffer.push(parent_full)
            return

        # Infinite capacity: FIFO semantics (take from current pointer forward; initial copy uses head)
        if self.parent_ref.buffer.capacity == AgentConfig.INFINITE_CAPACITY:
            if not prev_full or not any(isinstance(prev_full.get(k), list) for k in list_cols):
                total = len(parent_full[list_cols[0]])
                take = total if self.n == 0 else min(self.n, total)
                # Head slice preserves original arrival order (FIFO)
                data = {k: (v[0:take] if isinstance(v, list) else v) for k, v in parent_full.items()}
                self.pointer += take
                self.buffer.push(data)
                return
            total_parent = len(parent_full[list_cols[0]])
            new_available = total_parent - self.pointer
            if new_available <= 0:
                return
            take = new_available if self.n == 0 else min(self.n, new_available)
            start = self.pointer
            end = start + take
            data = {k: (v[start:end] if isinstance(v, list) else v) for k, v in parent_full.items()}
            self.pointer += take
            self.buffer.push(data)
            return

        # Finite capacity: window pattern match to find overlap, then take new rows from tip of new segment
        common_cols = [k for k in list_cols if isinstance(prev_full.get(k), list)]
        if not prev_full or not common_cols:
            # First run or no overlap columns: take head respecting n (FIFO)
            total = len(parent_full[list_cols[0]])
            take = total if self.n == 0 else min(self.n, total)
            data = {k: (v[0:take] if isinstance(v, list) else v) for k, v in parent_full.items()}
            self.pointer += take
            self.buffer.push(data)
            return

        def rows(dct, cols):
            L = len(dct[cols[0]])
            return [tuple(dct[c][i] for c in cols) for i in range(L)]

        prev_rows = rows(prev_full, common_cols)
        parent_rows = rows(parent_full, common_cols)
        # Dynamic window: at least 3, half of previous rows, capped by available length
        window = min(max(3, len(prev_rows)//2), len(prev_rows))
        pattern = prev_rows[-window:]
        match_index = -1
        for i in range(len(parent_rows) - window, -1, -1):
            if parent_rows[i:i + window] == pattern:
                match_index = i
                break
        new_start = (match_index + window) if match_index != -1 else 0

        total_parent = len(parent_full[list_cols[0]])
        if new_start >= total_parent:
            return

        # Skip push if this would just duplicate the entire current parent (no new data)
        # Condition: full overlap (new_start == 0) AND identical row tuples
        if new_start == 0 and prev_rows == parent_rows:
            return

        available_new = total_parent - new_start
        take = available_new if self.n == 0 else min(self.n, available_new)
        if take <= 0:
            return

        self._slice_start = new_start
        self._slice_end = new_start + take
        data = {}
        for k, v in parent_full.items():
            if isinstance(v, list):
                data[k] = v[self._slice_start:self._slice_end]
            else:
                data[k] = v

        self._new_count = len(data[list_cols[0]]) if list_cols else 0
        if self._new_count == 0:
            return
        self.pointer += self._new_count
        self.buffer.push(data)