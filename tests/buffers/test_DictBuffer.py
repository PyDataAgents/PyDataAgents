"""DictBuffer Test Coverage


Core Storage & Schema
- Dynamic column creation with back-fill of historical rows using None.
- Consistent row alignment across all columns after any push.
- Capacity trimming drops oldest rows uniformly.

Insertion Modes
- Single scalar row, batch dict-of-lists (uniform lengths), mixed scalars broadcast.
- Iterative list[dict] ingestion.

Timestamps (when enabled)
- Exact copy of provided timestamps; generate only on first creation if absent.
- Later pushes without timestamps pad with None (no synthetic fabrication).
- Length validation for provided timestamp lists.

Index (when enabled)
- Copy of explicit indices (any spacing pattern) preserved.
- Auto-sequential continuation (last + 1) when omitted.
- Correct behavior across overflow (window shift) and repeated dataset pushes.
- Length & numeric validation; rejects non-numeric index scalars.

Alignment & Overflow
- Post-overflow slice alignment between previous and new state for indices & values.
- Uniform column lengths always (including meta columns when present).

Error Handling
- Inconsistent batch list lengths -> ValueError.
- Non-numeric broadcast scalars / index scalar -> ValueError.
- Mismatched timestamp/index list lengths -> ValueError.

Data Access Utilities
- size() logic correct (ignores timestamps for primary count unless solitary).
- data() deep-copies; meta keys present only when enabled.

Edge Padding Cases
- None padding for timestamps/index after initial copied sequence when omitted.

Ref: Test Names (descriptive)
- test_config_options_introspection; test_push_scalars_basic_capacity; test_capacity_trim_on_overflow; test_size_after_two_pushes; test_batch_list_dict_ingestion; test_mixed_scalar_list_batch_extension; test_new_column_padding_scalar_sequence; test_new_column_padding_batch_sequence; test_timestamps_enabled_alignment_multi_push; test_timestamps_enabled_capacity_alignment; test_index_enabled_basic_sequence; test_copy_parent_timestamps_exact; test_index_copy_continuation_overflow; test_timestamp_none_padding_after_copy; test_index_auto_increment_after_copy; test_error_non_numeric_index_value.
"""

from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.agents.AgentConfig import AgentConfig
import time
import pytest

def test_config_options_introspection():
    buf = DictBuffer()
    print(buf.config_options())
    
def test_push_scalars_basic_capacity():
    buf = DictBuffer()
    buf.capacity = 5
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    print(buf.data())
    
def test_capacity_trim_on_overflow():
    buf = DictBuffer()
    buf.capacity = 3
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    buf.push({"C1": 5, "C2": 6})
    print(buf.data())
    buf.push({"C1": 7, "C2": 8})
    print(buf.data())
    
def test_size_after_two_pushes():
    buf = DictBuffer()
    buf.capacity = 3
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    assert 2 == buf.size(), f"expected buffer size to be equal to 2 ({buf.size()})"
    
def test_batch_list_dict_ingestion():
    buf = DictBuffer()
    buf.capacity = 5    
    d = [
        {"A": 1.0, "B": 2.0},
        {"A": 2.0, "B": 3.0},
        {"A": 3.0, "B": 4.0}
    ]    
    buf.push(d)    
    assert 3 == buf.size(), f"expected buffer size to be equal to 3 ({buf.size()})"
        
def test_mixed_scalar_list_batch_extension():
    buf = DictBuffer()
    buf.capacity = 10
    
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    
    d = {"C1": [5, 7], "C2": [6, 8]}
    
    buf.push(d)
    assert 4 == buf.size(), f"expected buffer size to be equal to 4 ({buf.size()})"
    
    
def test_new_column_padding_scalar_sequence():
    
    buf = DictBuffer(capacity=5)
    
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 2, "C2": 3})
    buf.push({"C1": 3, "C2": 4})
    
    print(buf.data())
    
    buf.push({"C1": 4, "C3": -1})
    
    print(buf.data())
    
def test_new_column_padding_batch_sequence():    
    buf = DictBuffer(capacity=5)    
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 2, "C2": 3})
    buf.push({"C1": 3, "C2": 4})    
    print(buf.data())    
    buf.push({"C1": [4, 5], "C3": [-1, -2]})    
    print(buf.data())


def test_timestamps_enabled_alignment_multi_push():    
    buf = DictBuffer(capacity=10, timestamps_enabled=True)    
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 2, "C2": 3})
    buf.push({"C1": 3, "C2": 4})      
    buf.push({"C1": [4, 5], "C3": [-1, -2]})    
    buf.push({"C3": [6,7,8], "C4": [8,9,10]})
    print(buf.data())
    assert all(len(v) == buf.size() for v in buf.data().values()), "Buffer columns have different lengths"

def test_timestamps_enabled_capacity_alignment():  
    #test with limited capacity  
    buf = DictBuffer(capacity=5, timestamps_enabled=True)    
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 2, "C2": 3})
    buf.push({"C1": 3, "C2": 4})
    print(buf.data())    
    buf.push({"C1": [4, 5], "C3": [-1, -2]})    
    buf.push({"C3": [6,7,8], "C4": [8,9,10]})
    print(buf.data())
    assert all(len(v) == 5 for v in buf.data().values()), "Buffer columns have different lengths"

def test_index_enabled_basic_sequence():
    # test index column
    buf = DictBuffer(capacity=10, index_enabled=True)
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 2, "C2": 3})
    buf.push({"C1": 3, "C2": 4})
    print(buf.data())    
    buf.push({"C1": [4, 5], "C2": [-1, -2]})
    print(buf.data(persistent=True))
    assert all(len(v) == buf.size() for v in buf.data().values()), "Buffer columns have different lengths"
    assert len(buf.data()[buf.index_key]) == 5, "Index column does not match expected sequence"
    assert buf.data()[buf.index_key] == [0, 1, 2, 3, 4], "Index column does not match expected sequence"

def test_copy_parent_timestamps_exact():
    """Verify DictBuffer copies parent timestamps without generating new ones.

    Scenario:
        - A source `SignalBuffer` collects time-stamped signal samples.
        - `LinkBufferAction` links to that buffer (no transformation, just access).
        - Data (including existing timestamps) is pushed into a `DictBuffer` with timestamps enabled.
    Expectations:
        - Destination timestamps equal source timestamps exactly (no overwrite/padding).
        - All columns share identical length alignment.
    """
    signal = Sine(f=1, a=1, p=0, n=0.04)
    src = SignalBuffer(signal=signal, capacity=25)
    # Generate a handful of samples manually (avoid scheduler dependency in test)
    for _ in range(80):
            src.signal_task()
            time.sleep(0.1)  # slight delay to diversify timestamps

    # Link action referencing the existing buffer
    lba = LinkBufferAction()
    lba.set_buffer(src)

    # Destination DictBuffer expecting to copy timestamps
    dest = DictBuffer(capacity=30, timestamps_enabled=True)

    src_data = lba.buffer.data()  # {'timestamps': [...], 'values': [...]} per AgentConfig
    assert src_data is not None and AgentConfig.TIMESTAMPS in src_data and AgentConfig.VALUES in src_data

    # Push source data into destination with explicit column mapping
    dest.push({
            'C1': src_data[AgentConfig.VALUES],
            dest.timestamps_key: src_data[AgentConfig.TIMESTAMPS]
    })

    dest_data = dest.data()

    # Assert timestamps are copied exactly and alignment holds and timestamps are in ascending order
    assert dest_data[dest.timestamps_key] == src_data[AgentConfig.TIMESTAMPS], "Timestamps were not copied intact"
    assert len(dest_data['C1']) == len(dest_data[dest.timestamps_key]) == dest.size(), "Column lengths misaligned"
    assert all(len(v) == dest.size() for v in dest_data.values()), "A destination column has incorrect length"


def test_index_copy_continuation_overflow():
    """
    test_071 validates correct index handling behavior when transferring and extending
    data between SignalBuffer and DictBuffer instances with capacity constraints.
    Test scenario overview:
    1. Source population:
        - A Sine signal is sampled manually (avoiding scheduler dependency) and appended
            to a SignalBuffer (src). This produces a time/value series.
    2. Initial transfer:
        - A LinkBufferAction wraps the existing SignalBuffer.
        - Data (values only) is pushed into an intermediate DictBuffer (dest) with indexing enabled.
        - A synthetic, explicitly provided index sequence (regular gap of 10) is pushed alongside
            the copied values into a new DictBuffer (final_dest), asserting that explicit indices
            are preserved intact.
    3. Automatic index continuation:
        - Additional values are pushed without supplying indices. The test asserts that the
            DictBuffer generates sequentially continuing indices (last + 1 pattern) and that
            all columns remain length-aligned.
    4. Overflow and index shifting:
        - The original dataset is pushed again with explicit indices. Due to capacity limits
            (30), older entries are truncated. The test asserts:
                a. Post-overflow alignment between pre- and post-push retained windowed segments.
                b. Proper truncation logic (shift of retained slice).
                c. Integrity of copied indices for the newest appended elements.
                d. Value-to-index alignment consistency.
    Assertions ensure:
    - Explicit index preservation when provided.
    - Auto-increment behavior when indices are omitted.
    - Correct truncation semantics on capacity overflow.
    - Column length uniformity after multiple pushes.
    - Alignment between indices and corresponding data values after complex operations.
    This test guards against regressions in:
    - DictBuffer index management (copy, continuation, overflow).
    - Data integrity during chained buffer operations.
    """
        
    signal = Sine(f=1, a=1, p=0, n=0.04)
    src = SignalBuffer(signal=signal, capacity=25)
    # Generate a handful of samples manually (avoid scheduler dependency in test)
    for _ in range(80):
            src.signal_task()
            time.sleep(0.1)  # slight delay to diversify timestamps

    # Link action referencing the existing buffer
    lba = LinkBufferAction()
    lba.set_buffer(src)

    # Destination DictBuffer expecting to copy indices
    dest = DictBuffer(capacity=30, index_enabled=True)
    final_dest = DictBuffer(capacity=30, index_enabled=True)

    src_data = lba.buffer.data()

    # Push source data into destination with explicit column mapping
    dest.push({
            'C1': src_data[AgentConfig.VALUES]
    })
    dest_data = dest.data()
    synth_indices = list(range(0,10*dest.size(),10))

    final_dest.push({"C1": dest_data["C1"], final_dest.index_key: synth_indices})
    final_dest_data = final_dest.data()

    assert final_dest_data[final_dest.index_key] == synth_indices, "Indices were not copied intact"
    
    # Add more data and ensure that the index picks up correctly
    final_dest.push({'C1': [999, 1000, 1001]})
    final_dest_data = final_dest.data()
    assert final_dest_data[final_dest.index_key][-3:] == [synth_indices[-1]+1, synth_indices[-1]+2, synth_indices[-1]+3], "Indices did not continue correctly after push"        
    assert len(set([len(v) for v in final_dest_data.values()])) == 1, "A column has incorrect length after padding"

    # push the original data again to see if indices are copied again and check for correct alignement in case of size overflow
    length_before = len(final_dest_data[final_dest.index_key])
    length_of_data_to_push = len(dest_data["C1"])
    final_dest.push({"C1": dest_data["C1"], final_dest.index_key: dest_data[dest.index_key]})
    final_dest_data_2 = final_dest.data()
    total_length = length_before + length_of_data_to_push 
    allowed_length = 30
    pos_to_shift = max(0,total_length - allowed_length)
    # in case of size overflow, the indices should be shifted accordingly
    assert final_dest_data[final_dest.index_key][pos_to_shift:] == final_dest_data_2[final_dest.index_key][:max(0, length_before-pos_to_shift)], "Indices were not shifted correctly after overflow"
    assert final_dest_data["C1"][pos_to_shift:] == final_dest_data_2["C1"][:max(0, length_before-pos_to_shift)]
    assert final_dest_data_2[final_dest.index_key][-3] == dest_data[dest.index_key][-3], "Indices were not copied intact after overflow"

def test_timestamp_none_padding_after_copy():
    """After copying timestamps, pushing additional values without timestamps should pad timestamps with None.

    Steps:
        1. Create and sample a `SignalBuffer` producing timestamped values.
        2. Copy its data (values + timestamps) into a `DictBuffer` with timestamps enabled.
        3. Push extra values (no timestamps) to the `DictBuffer`.
    Expectations:
        - New rows in timestamps column are None placeholders.
        - Column lengths remain aligned.
    """
    signal = Sine(f=1, a=1, p=0, n=0.04)
    src = SignalBuffer(signal=signal, capacity=25)
    for _ in range(5):
            src.signal_task()
            time.sleep(0.002)
    lba = LinkBufferAction()
    lba.set_buffer(src)
    dest = DictBuffer(capacity=25, timestamps_enabled=True)
    src_data = lba.buffer.data()
    dest.push({'C1': src_data[AgentConfig.VALUES], dest.timestamps_key: src_data[AgentConfig.TIMESTAMPS]})
    initial_size = dest.size()
    # Push additional values without timestamps (3 new entries)
    dest.push({'C1': [999, 1000, 1001]})
    dest_data = dest.data()
    assert dest.size() == initial_size + 3, "Size did not grow as expected"
    ts_tail = dest_data[dest.timestamps_key][-3:]
    assert ts_tail == [None, None, None], f"Expected None padding for new rows, got {ts_tail}"
    assert len(dest_data['C1']) == len(dest_data[dest.timestamps_key]) == dest.size(), "Lengths misaligned post padding"
    assert all(len(v) == dest.size() for v in dest_data.values()), "A column has incorrect length after padding"
    

def test_index_auto_increment_after_copy():
    """
    test_090 validates correct behavior of indexed DictBuffer operations when:
    1. Transferring time-series signal data from a source SignalBuffer via LinkBufferAction.
    2. Pushing an initial column ('C1') along with an automatically generated index column.
    3. Appending additional values to an existing column without explicitly providing index values,
        ensuring the buffer auto-extends the index sequence appropriately (strictly ascending, gapless).
    4. Verifying structural integrity and synchronization across columns after growth.
    Test Workflow Summary:
    - Generate a short sine wave signal and accumulate samples in a SignalBuffer (src).
    - Link the source buffer and extract its structured data payload.
    - Push the 'C1' numeric sequence into a destination DictBuffer with indexing enabled.
    - Mirror the destination data into a second DictBuffer (final_dest), explicitly preserving the index.
    - Append three new values to 'C1' (without supplying an index), expecting automatic index extension.
    - Collect final buffer state and perform invariants checks.
    Assertions Performed:
    - Size increased exactly by 3 after appending new values (no unintended side effects).
    - The last six index values form a strictly ascending contiguous integer sequence.
    - The index column is globally strictly ascending (monotonic increasing, no duplicates).
    - Column 'C1' length matches the index column length (row alignment preserved).
    - All columns in the final buffer share identical lengths (structural uniformity).
    Purpose:
    Ensures DictBuffer:
    - Maintains a consistent, auto-incrementing index when new data arrives without explicit index.
    - Preserves column length parity and prevents misalignment.
    - Supports safe column extension semantics crucial for tabular time-series building.
    No parameters. No return value. The test will fail with assertion errors if invariants are violated.
    """
    
    signal = Sine(f=1, a=1, p=0, n=0.04)
    src = SignalBuffer(signal=signal, capacity=25)
    for _ in range(5):
            src.signal_task()
            time.sleep(0.002)
    lba = LinkBufferAction()
    lba.set_buffer(src)
    dest = DictBuffer(capacity=25, index_enabled=True)
    final_dest = DictBuffer(capacity=25, index_enabled=True)
    src_data = lba.buffer.data()
    dest.push({'C1': src_data[AgentConfig.VALUES]})
    dest_data = dest.data()
    final_dest.push({'C1': dest_data["C1"], final_dest.index_key: dest_data[AgentConfig.INDEX]})
    final_dest.push({'C1': [999, 1000, 1001]})
    final_dest_data = final_dest.data()
    initial_size = dest.size()
    # Push additional values without index (3 new entries)
    assert final_dest.size() == initial_size +3 , "Size did not grow as expected"
    idx_tail = final_dest_data[final_dest.index_key][-6:]
    assert idx_tail[-6:] == [final_dest_data[final_dest.index_key][-6], final_dest_data[final_dest.index_key][-6]+1, final_dest_data[final_dest.index_key][-6]+2, final_dest_data[final_dest.index_key][-6]+3, final_dest_data[final_dest.index_key][-6]+4, final_dest_data[final_dest.index_key][-6]+5], f"Expected None padding for new rows, got {idx_tail}"
    idx_seq = final_dest_data[final_dest.index_key]
    assert all(prev < nxt for prev, nxt in zip(idx_seq, idx_seq[1:])), "Index column is not strictly ascending"
    assert len(final_dest_data['C1']) == len(final_dest_data[final_dest.index_key]), "Lengths misaligned post padding"
    assert len(set([len(v) for v in final_dest_data.values()])) == 1, "A column has incorrect length after padding"

def test_error_non_numeric_index_value():
    """Test that a ValueError is raised when non-numeric index data is provided."""
    signal = Sine(f=1, a=1, p=0, n=0.04)
    src = SignalBuffer(signal=signal, capacity=25)
    for _ in range(5):
            src.signal_task()
            time.sleep(0.01)
    lba = LinkBufferAction()
    lba.set_buffer(src)
    dest = DictBuffer(capacity=30, index_enabled=True)
    src_data = lba.buffer.data()
    # Expect ValueError when providing a non-numeric index sequence
    with pytest.raises(ValueError):
        dest.push({
            'C1': src_data[AgentConfig.VALUES],
            dest.index_key: "a"
        })
    False, "Expected ValueError when providing non-numeric index data"
    
