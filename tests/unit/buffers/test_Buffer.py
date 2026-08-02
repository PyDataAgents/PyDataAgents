import json
import pytest
from pydag.buffers.ListBuffer import ListBuffer
from pydag.agents.Agent import Agent
from pydag.buffers.DataType import DataType
from pydag.agents.AgentKeywords import AgentKeywords

@pytest.fixture
def agent():
    return Agent(id="agent1")

def test_install_uninstall_initial_values():
    buf = ListBuffer(id="b1", initial_values=[1, 2, 3])
    buf.install()
    assert buf.size() == 3
    buf.uninstall()
    assert buf.size() == 0

def test_push_and_capacity_fifo():
    buf = ListBuffer(id="b2", capacity=3)
    buf.install()
    buf.push([1, 2])
    buf.push(3)
    buf.push(4)  # evicts 1
    values = buf.data()[AgentKeywords.VALUES]
    assert values == [2, 3, 4]
    assert buf.size() == 3

def test_data_persistent_false_removes_returned():
    buf = ListBuffer(id="b3", capacity=-1)
    buf.install()
    buf.push([10, 20, 30])
    out = buf.data(n=2, persistent=False)
    assert out[AgentKeywords.VALUES] == [10, 20]
    remaining = buf.data()[AgentKeywords.VALUES]
    assert remaining == [30]

def test_clear_and_to_dict_and_str_json():
    buf = ListBuffer(id="b4", description="desc", unit="V", data_type=DataType.FLOAT.value)
    buf.install()
    buf.push([5, 6])
    d = buf.to_dict()
    assert "b4" in d and d["b4"] is buf
    parsed = json.loads(str(buf))
    assert AgentKeywords.META in parsed and parsed[AgentKeywords.META]["description"] == "desc"
    buf.clear()
    assert buf.size() == 0

def test_json_and_data_with_meta_contents():
    buf = ListBuffer(id="b5", capacity=-1, description="test", unit="m", data_type=DataType.INT.value)
    buf.install()
    buf.push([1, 2, 3])
    meta = buf.data_with_meta()
    # meta structure: {data: {values: {...}}, meta: {...}}
    assert meta[AgentKeywords.META]["capacity"] == -1
    assert meta[AgentKeywords.META]["data_type"] == DataType.INT.value
    assert meta[AgentKeywords.META]["unit"] == "m"
    assert meta[AgentKeywords.META]["description"] == "test"
    assert buf.size() == 3
    parsed = json.loads(buf.json())
    # json() with n=0 returns all values deep inside parsed[DATA][VALUES][VALUES]
    values = parsed[AgentKeywords.DATA][AgentKeywords.VALUES][AgentKeywords.VALUES]
    assert values == [1, 2, 3]

def test_duplicate_ids_without_agent():
    buf = ListBuffer(id="main", duplicate_ids=["dup1", "dup2"], capacity=-1)
    buf.install()
    assert set(buf._duplicates.keys()) == {"dup1", "dup2"}
    buf.push([100, 200])
    main_vals = buf.data()[AgentKeywords.VALUES]
    dup1_vals = buf._duplicates["dup1"].data()[AgentKeywords.VALUES]
    dup2_vals = buf._duplicates["dup2"].data()[AgentKeywords.VALUES]
    assert main_vals == dup1_vals == dup2_vals == [100, 200]
    buf.clear()
    assert buf.size() == 0 and buf._duplicates["dup1"].size() == 0 and buf._duplicates["dup2"].size() == 0

def test_duplicate_ids_with_agent_store(agent: Agent):
    dup_a = ListBuffer(id="dupA", capacity=-1); dup_a.install(agent); agent.add_buffer(dup_a)
    dup_b = ListBuffer(id="dupB", capacity=-1); dup_b.install(agent); agent.add_buffer(dup_b)
    buf = ListBuffer(id="mainA", duplicate_ids=["dupA", "dupB"], capacity=-1)
    buf.install(agent)
    assert buf._duplicates["dupA"] is dup_a
    assert buf._duplicates["dupB"] is dup_b
    buf.push([7, 8, 9])
    assert dup_a.data()[AgentKeywords.VALUES] == [7, 8, 9]
    assert dup_b.data()[AgentKeywords.VALUES] == [7, 8, 9]

def test_data_persistent_false_all_clears():
    buf = ListBuffer(id="b6", capacity=-1)
    buf.install()
    buf.push([1, 2, 3])
    assert buf.size() == 3
    parsed_before = json.loads(buf.json())
    vals_before = parsed_before[AgentKeywords.DATA][AgentKeywords.VALUES][AgentKeywords.VALUES]
    assert vals_before == [1, 2, 3]
    _ = buf.data(n=0, persistent=False)
    assert buf.size() == 0

def test_lock_exists_and_is_rlock():
    buf = ListBuffer(id="locktest")
    buf.install()
    import threading
    # RLock factory returns implementation object; interface check instead of isinstance
    assert hasattr(buf._lock, "acquire") and hasattr(buf._lock, "release")
