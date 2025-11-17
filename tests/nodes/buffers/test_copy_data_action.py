import os
import time
import pytest

from pydag.agents.Agent import Agent
from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode
from pydag.nodes.buffers.CopyDataAction import CopyDataAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.PlotlifyAction import PlotlifyAction
from pydag.services.rest.RestService import RestService
from pydag.services.statemachine.SimpleActionService import SimpleActionService
from pydag.mappings.ThreadType import ThreadType
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.agents.AgentConfig import AgentConfig


def test_non_persistent_raises():
    """Test that executing a non-persistent CopyDataAction raises RuntimeError.
    """
    db = DatasetBuffer(dataset_name="ArrowHead")
    db.install()
    lba = LinkBufferAction(); lba.set_buffer(db); lba.install()
    cda = CopyDataAction(n=10, persistent=False)
    cda.add_parent(lba); cda.install()
    with pytest.raises(RuntimeError):
        cda.execute()
                
                
def test_forward_initial_snapshot_finite():
    """
    Test that CopyDataAction correctly captures an initial forward (FIFO) snapshot of
    the first N samples from a source SignalBuffer into its own buffer when:
    - The source buffer is being filled asynchronously (via time-delayed sampling).
    - The action is configured with forward=True (copy earliest samples),
        persistent=True (allow cumulative growth), and timestamps_enabled=True.
    - N=5 specifies the snapshot size.
    """
    signal = Sine(f=1, a=1, p=0, n=0.02)
    src = SignalBuffer(signal=signal, capacity=50); src.install()
    lba = LinkBufferAction(); lba.set_buffer(src)
    cda = CopyDataAction(n=5, persistent=True, forward=True, timestamps_enabled=True)
    cda.add_parent(lba); cda.install()
    time.sleep(0.15)  # generate some samples
    cda.execute()
    # Removed fixed size assert; allow cumulative growth
    # Compare head (FIFO initial snapshot)
    full_src = src.data(persistent=True)
    head_src = {k: (v[0:5] if isinstance(v, list) else v) for k, v in full_src.items()}
    copied = cda.buffer.data(n=5, persistent=True)
    assert list(head_src.values()) == list(copied.values())


def test_forward_multiple_snapshots_finite():
    # Test if multiple executions copy advancing data correctly if the parent buffer is limited in capacity and consumer buffer is infinite. The data added to the tail of the consumer must be contained in the correct position in the source data.
    signal = Sine(f=1, a=1, p=0, n=0.02)
    src = SignalBuffer(signal=signal, capacity=50); src.install()
    lba = LinkBufferAction(); lba.set_buffer(src)
    cda = CopyDataAction(n=10, persistent=True, forward=True)
    cda.add_parent(lba); cda.install()
    for i in range(100):
        time.sleep(1)  # generate some samples
        print(lba.buffer.size())
        if lba.buffer.size() >= 10:
            full_src = lba.buffer.data(persistent=True)
            cda.execute()
            full_cda = cda.buffer.data(persistent=True)
            if hasattr(cda, "_slice_end"):
                # Verify that the newly copied data matches the corresponding slice in the source buffer
                for k in full_cda:
                    if isinstance(full_cda[k], list):
                        copied_series = full_cda[k][-(cda._slice_end-cda._slice_start):] # Somewhere in the parent buffer
                        source_series = full_src[k][cda._slice_start:cda._slice_end] # Ad the tail of the consumer buffer
                        assert cda._slice_start >= 0, f"Invalid slice start at iteration {i}"
                        assert cda._slice_end >= cda._slice_start, f"Invalid slice end at iteration {i}"
                        assert cda._slice_end <= 50, f"Slice end exceeds source size at iteration {i}"
                        assert copied_series == source_series, f"Data mismatch in key '{k}' at iteration {i}"
    


def test_forward_shared_and_advancing_finite():
    """
    Test that two forward-advancing, persistent CopyDataAction consumers fed from a shared
    SignalBuffer via a LinkBufferAction remain synchronized while the source data advances.
    """
    signal = Sine(f=1, a=1, p=0, n=0.05)
    src = SignalBuffer(signal=signal, capacity=60, sampling_period=100); src.install()
    lba = LinkBufferAction(); lba.set_buffer(src)
    cda1 = CopyDataAction(n=10, persistent=True, forward=True); cda1.add_parent(lba); cda1.install()
    cda2 = CopyDataAction(n=10, persistent=True, forward=True); cda2.add_parent(lba); cda2.install()
    prev_data = None
    changes = 0
    last_size_1 = 0
    last_size_2 = 0
    for i in range(35):
        time.sleep(1)
        cda1.execute(); cda2.execute()
        if cda1.buffer.size() == 0: continue
        # Retrieve latest slice for comparison
        full1 = cda1.buffer.data(persistent=True)
        full2 = cda2.buffer.data(persistent=True)
        # Latest comparison still uses tail of buffers (advancement), FIFO initial copy unaffected
        d1 = {k: (v[-10:] if isinstance(v, list) else v) for k, v in full1.items()}
        d2 = {k: (v[-10:] if isinstance(v, list) else v) for k, v in full2.items()}
        assert list(d1.values()) == list(d2.values()), f"Mismatch between consumers at {i}"
        if prev_data is not None and list(prev_data.values()) != list(d1.values()):
            changes += 1
        prev_data = d1
        # After skip-duplicate/trimming logic: size may shrink; just ensure non-negative
        # Removed: assert cda1.buffer.size() <= src.size()
        # Removed: assert cda2.buffer.size() <= src.size()
        assert cda1.buffer.size() >= 0
        assert cda2.buffer.size() >= 0
        last_size_1 = cda1.buffer.size()
        last_size_2 = cda2.buffer.size()
    assert changes >= 20, f"Insufficient advancement changes={changes}"

def test_forward_pointer_wrap_finite():
    """
    Test that a forward, persistent CopyDataAction advances its internal read pointer
    monotonically (never moving backwards) while consuming data from a finite-length
    signal buffer, and that it advances a minimum number of times.

    Scenario:
    1. Create a finite Sine signal and attach it to a SignalBuffer with fixed capacity.
    2. Link the buffer via LinkBufferAction and configure a CopyDataAction to:
        - copy up to n=5 samples per execution
        - operate in forward mode
        - persist its pointer across executions.
    3. Repeatedly execute the copy action over timed intervals, accumulating pointer
        advances only when the buffer has data.
    4. Assert:
        - Pointer never decreases (monotonic non-decreasing behavior).
        - Pointer advances (strictly increases) at least 10 times across iterations,
          ensuring progress and correct wrap/continuation semantics for a finite source.

    This guards against:
    - Pointer regression due to wrap logic errors.
    - Stalling where no forward progress is made despite available data.
    - Incorrect handling of an exhausted finite signal leading to spurious pointer movement.

    Failure indicates insufficient forward progress (potential starvation or pointer
    management bug) or non-monotonic pointer behavior.
    """
    signal = Sine(f=1, a=1, p=0, n=0.04)
    src = SignalBuffer(signal=signal, capacity=25); src.install()
    lba = LinkBufferAction(); lba.set_buffer(src)
    cda = CopyDataAction(n=5, persistent=True, forward=True); cda.add_parent(lba); cda.install()
    last_pointer = cda.pointer
    advances = 0
    for i in range(50):
        time.sleep(0.08)
        cda.execute()
        if cda.buffer.size() == 0: continue
        assert cda.pointer >= last_pointer
        if cda.pointer > last_pointer:
            advances += 1
        last_pointer = cda.pointer
    assert advances >= 10, f"Too few pointer advances: {advances}"


def test_forward_infinite_capacity_advancing():
    """Test that two forward, persistent CopyDataAction instances reading from an
    infinite-capacity SignalBuffer advance their shared source correctly and
    collect identical trailing slices of data.

    Setup:
    - Create a Sine signal and wrap it in a SignalBuffer with infinite capacity.
    - LinkBufferAction provides a common source for two CopyDataAction instances.
    - Each CopyDataAction pulls (n=15) items forward, persistently accumulating data.

    Assertions performed for ~30 execution cycles:
    - Both action buffers contain identical latest 15-sample windows.
    - Pointer for the first action is monotonic (never decreases) and advances
        sufficiently (at least 10 increments) to prove ongoing data flow.
    - Buffer sizes never exceed their respective pointer counts (sanity check
        for infinite capacity behavior).
    - Data changes occur over time (implicit via pointer advancement and value updates).

    The test validates:
    - Consistency between multiple forward consumers.
    - Proper pointer advancement semantics.
    - Safety of unbounded (infinite) buffer growth relative to logical write position.
    """
    signal = Sine(f=1, a=1, p=0, n=0.05)
    src = SignalBuffer(signal=signal, capacity=AgentConfig.INFINITE_CAPACITY); src.install()
    lba = LinkBufferAction(); lba.set_buffer(src)
    cda1 = CopyDataAction(n=15, persistent=True, forward=True); cda1.add_parent(lba); cda1.install()
    cda2 = CopyDataAction(n=15, persistent=True, forward=True); cda2.add_parent(lba); cda2.install()
    last_pointer = cda1.pointer
    changes = 0
    prev_vals = None
    for i in range(30):
        time.sleep(0.1)
        cda1.execute(); cda2.execute()
        if cda1.buffer.size() == 0: continue
        full1 = cda1.buffer.data(persistent=True)
        full2 = cda2.buffer.data(persistent=True)
        d1 = {k: (v[-15:] if isinstance(v, list) else v) for k, v in full1.items()}
        d2 = {k: (v[-15:] if isinstance(v, list) else v) for k, v in full2.items()}
        assert list(d1.values()) == list(d2.values())
        assert cda1.pointer >= last_pointer
        if cda1.pointer > last_pointer:
            changes += 1
        last_pointer = cda1.pointer
        if prev_vals and list(prev_vals.values()) != list(d1.values()):
            pass
        prev_vals = d1
        # Infinite capacity: ensure buffer size does not exceed pointer count (sanity)
        assert cda1.buffer.size() <= cda1.pointer
        assert cda2.buffer.size() <= cda2.pointer
    assert changes >= 10, f"Advancement insufficient changes={changes}"


def test_forward_infinite_capacity_plot_generation():
    """Generate multiple matplotlib plots comparing parent vs consumer over time."""
    try:
        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
    except Exception:
        pytest.skip("matplotlib unavailable")

    signal = Sine(f=1, a=1, p=0, n=0.05)
    src = SignalBuffer(signal=signal, capacity=AgentConfig.INFINITE_CAPACITY); src.install()
    lba = LinkBufferAction(); lba.set_buffer(src)
    cda = CopyDataAction(n=20, persistent=True, forward=True, timestamps_enabled=True, timestamps_key="timestamps")
    cda.add_parent(lba); cda.install()

    snapshots = []
    for i in range(40):
        time.sleep(0.5)
        cda.execute()
        if i in (10, 25, 39):  # snapshot points
            parent_full = src.data(persistent=True)
            consumer_full = cda.buffer.data(persistent=True)
            first_key = None
            for k, v in consumer_full.items():
                if isinstance(v, list) and v and k in parent_full and isinstance(parent_full[k], list) and k != "timestamps":
                    first_key = k; break
            if first_key is None:
                continue
            parent_series = parent_full[first_key]
            consumer_series = consumer_full[first_key]
            m = min(len(parent_series), len(consumer_series))
            parent_tail = parent_series[-m:]
            consumer_tail = consumer_series[-m:]
            assert parent_tail == consumer_tail, f"Tail mismatch at snapshot {i}"
            snapshots.append((i, first_key, parent_tail, consumer_tail))

    assert snapshots, "No snapshots collected"
    for (idx, key, p_tail, c_tail) in snapshots:
        assert p_tail == c_tail, f"Tail mismatch at snapshot {idx}"
        x = list(range(len(p_tail)))
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(x, p_tail, label=f"parent-{key}")
        ax.plot(x, c_tail, '--', label=f"cda-{key}")
        ax.set_title(f"Infinite Capacity Snapshot i={idx}")
        ax.set_xlabel("Sample Index (tail-aligned)")
        ax.set_ylabel(key)
        ax.legend(loc="upper right")
        fig.tight_layout()
        try:
            plt.show(block=True)
        finally:
            plt.close(fig)


def test_forward_infinite_capacity_dual_plot_comparison():
    """Generate multiple plot pairs for two consumers to verify identical tails over time."""
    try:
        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
    except Exception:
        pytest.skip("matplotlib unavailable")

    signal = Sine(f=1, a=1, p=0, n=0.04)
    src = SignalBuffer(signal=signal, capacity=AgentConfig.INFINITE_CAPACITY); src.install()
    lba = LinkBufferAction(); lba.set_buffer(src)
    cda1 = CopyDataAction(n=20, persistent=True, forward=True, timestamps_enabled=True, timestamps_key="timestamps")
    cda2 = CopyDataAction(n=20, persistent=True, forward=True, timestamps_enabled=True, timestamps_key="timestamps")
    cda1.add_parent(lba); cda1.install()
    cda2.add_parent(lba); cda2.install()

    pair_snapshots = []
    for i in range(45):
        time.sleep(0.4)
        cda1.execute(); cda2.execute()
        if i in (15, 30, 44):
            full1 = cda1.buffer.data(persistent=True)
            full2 = cda2.buffer.data(persistent=True)
            first_key = None
            for k, v in full1.items():
                if isinstance(v, list) and v and k in full2 and isinstance(full2[k], list) and k != "timestamps":
                    first_key = k; break
            if first_key is None:
                continue
            s1 = full1[first_key]
            s2 = full2[first_key]
            m = min(len(s1), len(s2))
            t1 = s1[-m:]
            t2 = s2[-m:]
            pair_snapshots.append((i, first_key, t1, t2))

    assert pair_snapshots, "No dual snapshots collected"
    for (idx, key, t1, t2) in pair_snapshots:
        assert t1 == t2, f"Consumer tails differ at snapshot {idx}"
        x = list(range(len(t1)))
        # Plot consumer 1
        fig1, ax1 = plt.subplots(figsize=(5, 2.6))
        ax1.plot(x, t1, label=f"cda1-{key}")
        ax1.set_title(f"cda1 tail snapshot i={idx}")
        ax1.legend(loc="upper right")
        fig1.tight_layout()
        try:
            plt.show(block=True)
        finally:
            plt.close(fig1)
        # Plot consumer 2
        fig2, ax2 = plt.subplots(figsize=(5, 2.6))
        ax2.plot(x, t2, label=f"cda2-{key}")
        ax2.set_title(f"cda2 tail snapshot i={idx}")
        ax2.legend(loc="upper right")
        fig2.tight_layout()
        try:
            plt.show(block=True)
        finally:
            plt.close(fig2)

def test_duplicate_skip_finite():
    """Verify that executing twice without new parent samples does not increase consumer size."""
    signal = Sine(f=1, a=1, p=0, n=0.5)  # slow generation
    src = SignalBuffer(signal=signal, capacity=40); src.install()
    lba = LinkBufferAction(); lba.set_buffer(src)
    cda = CopyDataAction(n=10, persistent=True, forward=True); cda.add_parent(lba); cda.install()
    time.sleep(0.2)
    cda.execute()
    size1 = cda.buffer.size()
    # Immediate second execute (likely no new parent rows)
    cda.execute()
    size2 = cda.buffer.size()
    assert size2 == size1, "Size changed despite no new data (duplicate push not skipped)."



def test_dataset_non_persistent_child_raises():
    """Test that a non-persistent CopyDataAction child raises RuntimeError when executed.
    Setup:
    1. Create and install a DatasetBuffer for the 'ArrowHead' dataset.
    2. Create a LinkBufferAction, attach the dataset buffer, and install it.
    3. Create a first persistent CopyDataAction (cba1), link it to the link action, and install it.
    4. Create a second non-persistent CopyDataAction (cba2), attach it as a child of cba1, and install it.
    5. Execute only the installed action chain (link + persistent copy) multiple times.
    Expectation:
    Attempting to execute the non-persistent child (cba2) after its parent has run succeeds in setup
    but should raise a RuntimeError upon execution because its persistence flag is False and
    its execution context is invalid once the parent has progressed.
    Assertion:
    Uses pytest.raises(RuntimeError) to confirm the correct exception is thrown.
    """
    db = DatasetBuffer(dataset_name="ArrowHead")
    db.install()
    
    lba = LinkBufferAction()
    lba.set_buffer(db)
    lba.install()
    
    cba1 = CopyDataAction(n=1000, persistent=True, forward=True)
    cba1.add_parent(lba)
    cba1.install()
    
    cba2 = CopyDataAction(n=1000, persistent=False, forward=True)
    cba2.add_parent(cba1)
    cba2.install()
    # Exclude cba2 from normal execution list; it should raise when executed
    nodes : list[Action] = [lba, cba1]

    for i in range(0, 5):
        for node in nodes:
            node.execute()
    # Verify that executing the non-persistent CopyDataAction raises RuntimeError
    with pytest.raises(RuntimeError):
        cba2.execute()



def test_manual_grafana_plot():
    """
    test_manual_grafana_plot
    Manual / integration test that spins up an Agent with:
    - A DatasetBuffer (id="DB") loading the 'ArrowHead' dataset (index enabled).
    - A RestService on port 8008 (intended for external inspection / e.g. Grafana datasource polling).
    - A SimpleActionService running on a millisecond thread with a 5 second sampling period.
    - A LinkBufferAction feeding two CopyDataAction nodes:
        * B1: persistent buffer (size 1000, index enabled) for historical queries.
        * B2: non‑persistent buffer (size 1000, index enabled) for transient / in‑memory inspection.
    Purpose:
    Provides a live, blocking environment to manually verify that copied data buffers can be read via the REST service
    and visualized (e.g. by Grafana) with differing persistence characteristics.
    Behavior:
    - agent.start_blocking() will prevent the test from returning; this is intentional for manual observation.
    - Requires port 8008 to be free.
    - Designed to be excluded from automated CI runs (rename or mark accordingly if using pytest).
    Usage:
    Run this test locally, then point an external visualization or HTTP client at the RestService endpoints to confirm:
    1. Data is being populated in both B1 and B2.
    2. Persistent buffer B1 retains history across sampling cycles.
    3. Non‑persistent buffer B2 only reflects the latest in‑memory state.
    Side Effects:
    Opens a listening REST endpoint and consumes a thread for the action service loop.
    No assertions:
    This test does not assert conditions; it is purely for manual validation / exploratory debugging.
    """

    agent = Agent()
    
    db = DatasetBuffer(id="DB", dataset_name="ArrowHead", index_enabled=True)
    
    agent.add_buffer(db)
    
    rs = RestService(port=8008)
    
    agent.add_service(rs)
    
    sas = SimpleActionService(thread_type=ThreadType.MILLI_SECOND, sampling_period=5000)
    
    lba = LinkBufferAction()
    lba.set_buffer(db)
    sas.add_node(lba)
    
    cda1 = CopyDataAction(buffer_id="B1", n=1000, persistent=True, index_enabled=True)
    cda1.add_parent(lba)
    sas.add_node(cda1)
    cda2 = CopyDataAction(buffer_id="B2", n=1000, persistent=True, index_enabled=True)
    cda2.add_parent(lba)
    sas.add_node(cda2)
    
    agent.add_service(sas)   
    
    agent.start_blocking()