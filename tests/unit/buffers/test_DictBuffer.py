import numpy as np

from pydag.agents.AgentConfig import AgentConfig
from pydag.buffers.BufferException import BufferException
from pydag.buffers.DictBuffer import DictBuffer

def test_config_options_introspection():
    buf = DictBuffer()
    print(buf.config_options())
    
def test_push_scalars_basic_capacity():
    buf = DictBuffer(capacity = 5)
    buf.install()
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    print(buf.data())
    
def test_capacity_trim_on_overflow():
    buf = DictBuffer()
    buf.capacity = 3
    buf.install()
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    buf.push({"C1": 5, "C2": 6})
    print(buf.data())
    buf.push({"C1": 7, "C2": 8})
    print(buf.data())
    
def test_size_after_two_pushes():
    buf = DictBuffer()
    buf.capacity = 3
    buf.install()
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    assert 2 == buf.size(), f"expected buffer size to be equal to 2 ({buf.size()})"
    
def test_batch_list_dict_ingestion():
    buf = DictBuffer()
    buf.capacity = 5
    buf.install()    
    d = [
        {"A": 1.0, "B": 2.0},
        {"A": 2.0, "B": 3.0},
        {"A": 3.0, "B": 4.0}
    ]    
    buf.push(d)    
    assert 3 == buf.size(), f"expected buffer size to be equal to 3 ({buf.size()})"
        
def test_mixed_scalar_list_batch_extension():
    buf = DictBuffer(timestamps_enabled=True)
    buf.capacity = 10
    buf.install()
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    
    d = {"C1": [5, 7], "C2": [6, 8]}
    
    buf.push(d)
    assert 4 == buf.size(), f"expected buffer size to be equal to 4 ({buf.size()})"
    
    
def test_new_column_padding_scalar_sequence():
    
    buf = DictBuffer(capacity=5)
    buf.install()
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 2, "C2": 3})
    buf.push({"C1": 3, "C2": 4})
    
    print(buf.data())
    
    buf.push({"C1": 4, "C3": -1})
    
    print(buf.data())
    
def test_new_column_padding_batch_sequence():    
    buf = DictBuffer(capacity=5)
    buf.install()    
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 2, "C2": 3})
    buf.push({"C1": 3, "C2": 4})    
    print(buf.data())    
    buf.push({"C1": [4, 5], "C3": [-1, -2]})    
    print(buf.data())


def test_timestamps_enabled_alignment_multi_push():    
    buf = DictBuffer(capacity=10, timestamps_enabled=True)
    buf.install()    
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
    buf.install()   
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
    buf.install()
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 2, "C2": 3})
    buf.push({"C1": 3, "C2": 4})
    print(buf.data())    
    buf.push({"C1": [4, 5], "C2": [-1, -2]})
    print(buf.data(persistent=True))
    assert all(len(v) == buf.size() for v in buf.data().values()), "Buffer columns have different lengths"
    assert len(buf.data()[buf.index_key]) == 5, "Index column does not match expected sequence"
    assert buf.data()[buf.index_key] == [0, 1, 2, 3, 4], "Index column does not match expected sequence"

def test_index_enabled_with_existing_empty_index_column():
    buf = DictBuffer(capacity=5, index_enabled=True)
    buf.install()
    # precreate empty index column by pushing a new column without data through alignment
    buf.push({"C1": 1})
    # now elements have index [0]; next batch_len=2 should extend properly
    buf.push({"C1": [2,3]})
    data = buf.data()
    assert data[buf.index_key] == [0, 1, 2], "Index should extend even when existing index column was empty initially"

def test_index_enabled_parent_provides_index():
    buf = DictBuffer(capacity=10, index_enabled=True, index_key="idx")
    buf.install()
    # parent provides index column; DictBuffer should accept and align
    buf.push({"C1": [10, 11], "idx": [5,6]})
    # next push without index should continue from last provided
    buf.push({"C1": [12, 13]})
    data = buf.data()
    assert data["idx"] == [5,6,7,8], "Index should continue after parent-provided indices"

def test_timestamps_enabled_auto_generation_and_alignment():
    buf = DictBuffer(capacity=5, timestamps_enabled=True)
    buf.install()
    buf.push({"C1": [2,3]})
    buf.push({"C1": 1})
    data = buf.data()
    assert buf.timestamps_key in data, "Timestamps column missing when enabled"
    assert len(data[buf.timestamps_key]) == buf.size(), "Timestamps length does not match buffer size"

def test_timestamps_enabled_parent_provided_and_mismatch_padding():
    buf = DictBuffer(capacity=10, timestamps_enabled=True)
    buf.install()
    # provide timestamps for first batch
    buf.push({"C1": [1,2], buf.timestamps_key: [100, 200]})
    # second batch without timestamps should pad or generate consistent length
    buf.push({"C1": [3,4,5]})
    data = buf.data()
    assert len(data[buf.timestamps_key]) == buf.size(), "Timestamps must align after mixed provision"

def test_timestamps_disabled_ignores_provided_column():
    buf = DictBuffer(capacity=10, timestamps_enabled=False)
    buf.install()
    buf.push({"C1": [1,2], buf.timestamps_key: [100,200]})
    data = buf.data()
    assert buf.timestamps_key not in data, "Timestamps should not be present when disabled"

def test_index_disabled_ignores_provided_column():
    buf = DictBuffer(capacity=10, index_enabled=False, index_key="idx")
    buf.install()
    buf.push({"C1": [1,2], "idx": [0,1]})
    data = buf.data()
    assert "idx" not in data, "Index should not be present when disabled"

def test_pushing_multiple_dicts():
    # test pushing a list of dictionaries (batch of individual rows)
    buf = DictBuffer(capacity=10)
    buf.install()
    batch = [
        {"C1": 1, "C2": 2},
        {"C1": 3, "C2": 4},
        {"C1": 5, "C2": 6}
    ]
    buf.push(batch)
    assert buf.size() == 3, f"expected buffer size to be equal to 3 ({buf.size()})"
    data = buf.data()
    assert data["C1"] == [1, 3, 5], f"unexpected C1 column data ({data['C1']})"
    assert data["C2"] == [2, 4, 6], f"unexpected C2 column data ({data['C2']})"
    # push another dict to ensure subsequent single insert works after list batch
    buf.push({"C1": 7, "C2": 8})
    data2 = buf.data()
    assert data2["C1"] == [1, 3, 5, 7] and data2["C2"] == [2, 4, 6, 8], "Data after single push does not match expected sequence"


def test_push_non_dict():
    # test pushing a list of dictionaries (batch of individual rows)
    buf = DictBuffer(capacity=10)
    buf.install()
    buf.push({"a": 1.0})
    buf.push(2.0)
    
    d = buf.data()
    assert len(d["a"]) == 2, "data should be of size 2"
    
def test_push_non_dict_list():
    # test pushing a list of dictionaries (batch of individual rows)
    buf = DictBuffer(capacity=10)
    buf.install()
    buf.push({"a": 1.0})
    buf.push([2.0, 3.0])
    
    d = buf.data()
    assert len(d["a"]) == 3, "data should be of size 3"

def test_push_non_dict_list2():
    # test pushing a list of dictionaries (batch of individual rows)
    buf = DictBuffer(capacity=10)
    buf.install()
    buf.push([1.0, 2.0, 3.0, 4.0])
    
    d = buf.data()
    assert AgentConfig.VALUES in d, "data key should be " + AgentConfig.VALUES
    assert len(d[AgentConfig.VALUES]) == 4, "data should be of size 4"

def test_push_non_dict_exception():
    # test pushing a list of dictionaries (batch of individual rows)
    buf = DictBuffer(capacity=10)
    buf.install()
    buf.push({"a": 1.0, "b": 2.0})
    try:
        buf.push(1)
    except BufferException as e:
        assert isinstance(e, BufferException), f"expected BufferException but got {type(e)}"

def test_meta_only_inserts_are_rejected():
    # Meta-only payloads (only timestamps/index) should be ignored entirely.
    buf = DictBuffer(capacity=10, timestamps_enabled=True, index_enabled=True)
    buf.install()
    # Push only index → should not modify buffer
    buf.push({buf.index_key: [0, 1, 2]})
    assert buf.data() == {}, "Meta-only insert must not modify buffer contents"
    assert buf.size() == 0, "Buffer size must remain zero after meta-only insert"

    # Push only timestamps → should still not modify buffer
    buf.push({buf.timestamps_key: [100, 200]})
    assert buf.data() == {}, "Meta-only timestamps insert must not modify buffer contents"
    assert buf.size() == 0, "Buffer size must remain zero after timestamps-only insert"

    # Now push real data; verify normal behavior resumes
    buf.push({"C1": [10, 11], "C2": [20, 21]})
    data = buf.data()
    assert data["C1"] == [10, 11] and data["C2"] == [20, 21], "Data columns should reflect pushed values"
    assert buf.size() == 2, "Size should reflect real data rows only"

def test_meta_only_both_columns_are_rejected():
    # If both meta columns are provided without data, buffer should ignore.
    buf = DictBuffer(capacity=10, timestamps_enabled=True, index_enabled=True)
    buf.install()
    buf.push({buf.timestamps_key: [100, 200], buf.index_key: [0, 1]})
    assert buf.data() == {}, "Meta-only insert (timestamps + index) must not modify buffer contents"
    assert buf.size() == 0, "Buffer size must remain zero for meta-only payloads"
    # Follow up with real data to ensure normal behavior
    buf.push({"C1": 1, "C2": 2})
    assert buf.size() == 1, "After real data push, size should be 1"

def test_raised_value_when_incosistent_length_metadata_only():
    # Meta-only payloads with inconsistent lengths should raise ValueError before insertion.
    buf = DictBuffer(capacity=10, timestamps_enabled=True, index_enabled=True)
    buf.install()
    import pytest
    with pytest.raises(ValueError):
        buf.push({buf.timestamps_key: [100, 200], buf.index_key: [0, 1, 2]})

def test_timestamps_generated_on_subsequent_scalar_pushes():
    buf = DictBuffer(timestamps_enabled=True)
    buf.install()
    buf.push({"a": 1})
    buf.push({"a": 2})
    data = buf.data()
    ts = data.get(buf.timestamps_key)
    assert ts is not None
    assert len(ts) == 2
    assert all(t is not None for t in ts), "Timestamps should be generated, not None"

def test_timestamps_generated_on_subsequent_batch_pushes():
    buf = DictBuffer(timestamps_enabled=True)
    buf.install()
    buf.push({"a": [1, 2, 3]})
    buf.push({"a": [4, 5]})
    data = buf.data()
    ts = data.get(buf.timestamps_key)
    assert ts is not None
    assert len(ts) == 5
    assert all(t is not None for t in ts), "Timestamps should be generated, not None"

def test_timestamps_with_broadcasted_scalars():
    buf = DictBuffer(timestamps_enabled=True)
    buf.install()
    buf.push({"a": [1, 2, 3], "b": 9})
    data = buf.data()
    ts = data.get(buf.timestamps_key)
    assert ts is not None
    assert len(ts) == 3
    assert all(t is not None for t in ts)

def test_push_dict_with_empty_list():
    buf = DictBuffer(timestamps_enabled=True)
    buf.install()
    # Pushing an empty list should not change size and should not create misaligned columns
    buf.push({"a": []})
    assert buf.size() == 0, "Size should remain 0 when pushing empty list"
    assert buf.data() == {}, "Data should remain None after empty list push"

def test_timestamps_monotonicity_across_scalar_pushes():
    buf = DictBuffer(timestamps_enabled=True)
    buf.install()
    # push several scalars
    buf.push({"a": 1})
    buf.push({"a": 2})
    buf.push({"a": 3})
    ts = buf.data()[buf.timestamps_key]
    d = np.diff(ts)
    print(d)
    assert len(ts) == 3
    assert all(d > 0), "Timestamps must be strictly increasing across scalar pushes"

def test_timestamps_monotonicity_across_mixed_batches():
    buf = DictBuffer(timestamps_enabled=True)
    buf.install()
    # first batch
    buf.push({"a": [1, 2, 3]})
    # second scalar
    buf.push({"a": [4]})
    # third batch
    buf.push({"a": [5, 6]})
    ts = buf.data()[buf.timestamps_key]
    d = np.diff(ts)
    print(d)
    assert len(ts) == 6
    # ensure strictly increasing timestamps throughout
    assert all(ts[i] < ts[i+1] for i in range(len(ts)-1)), "Timestamps must be strictly increasing across mixed pushes"


def test_timestamps_mixed_provided_then_missing():
    buf = DictBuffer(timestamps_enabled=True)
    buf.install()
    import time as _time
    now = _time.time_ns()
    provided = [now, now -1 , now -2]
    buf.push({"a": [9, 10, 11], buf.timestamps_key: provided})
    buf.push({"a": [12]})
    buf.push({"a": [12, 14, 15]})
    data = buf.data()
    ts = data.get(buf.timestamps_key)
    assert ts is not None
    assert len(ts) == 7
    assert ts[:3] == provided
    assert ts[3] is not None, "Missing timestamps after provided ones should be generated"
    # ensure strictly increasing timestamps throughout
    assert all(ts[len(ts)-i-1] > ts[len(ts)-i-2] for i in range(4)), "Timestamps must be strictly increasing across mixed pushes"
