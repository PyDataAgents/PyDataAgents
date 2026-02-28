import json
import pytest
from pydag.buffers.ListBuffer import ListBuffer as TestBuffer
from pydag.agents.Agent import Agent
from pydag.buffers.DataType import DataType
from pydag.agents.AgentConfig import AgentConfig


@pytest.fixture
def agent():
    return Agent(id="agent1")


def test_install_uninstall_initial_values():
    buf = TestBuffer(id="b1", initial_values=[1, 2, 3])
    buf.install()
    assert buf.size() == 3
    buf.uninstall()
    assert buf.size() == 0


def test_push_and_capacity_fifo():
    buf = TestBuffer(id="b2", capacity=3)
    buf.install()
    buf.push([1, 2])
    buf.push(3)
    buf.push(4)  # should evict 1
    values = buf.data()[AgentConfig.VALUES]
    assert values == [2, 3, 4]
    assert buf.size() == 3


def test_data_persistent_false_removes_returned():
    buf = TestBuffer(id="b3", capacity=-1)
    buf.install()
    buf.push([10, 20, 30])
    out = buf.data(n=2, persistent=False)
    assert out[AgentConfig.VALUES] == [10, 20]
    remaining = buf.data()[AgentConfig.VALUES]
    assert remaining == [30]


def test_clear_and_to_dict_and_str_json():
    buf = TestBuffer(id="b4", description="desc", unit="V", data_type=DataType.FLOAT.value)
    buf.install()
    buf.push([5, 6])
    d = buf.to_dict()
    assert "b4" in d and d["b4"] is buf
    parsed = json.loads(str(buf))
    assert AgentConfig.DATA in parsed and AgentConfig.META in parsed
    assert parsed[AgentConfig.META]["description"] == "desc"
    buf.clear()
    assert buf.size() == 0


def test_json_and_data_with_meta_contents():
    buf = TestBuffer(id="b5", capacity=-1, description="test", unit="m", data_type=DataType.INT.value)
    buf.install()
    buf.push([1, 2, 3])
    meta = buf.data_with_meta()
    assert meta[AgentConfig.META]["capacity"] == -1
    assert meta[AgentConfig.META]["data_type"] == DataType.INT.value
    assert meta[AgentConfig.META]["unit"] == "m"
    assert meta[AgentConfig.META]["description"] == "test"
    assert buf.size() == 3
    parsed = json.loads(buf.json())
    values = parsed[AgentConfig.DATA][AgentConfig.VALUES][AgentConfig.VALUES]
    assert values == [1, 2, 3]


def test_duplicate_ids_without_agent():
    buf = TestBuffer(id="main", duplicate_ids=["dup1", "dup2"], capacity=-1)
    buf.install()
    assert set(buf.get_duplicates().keys()) == {"dup1", "dup2"}
    buf.push([100, 200])
    main_vals = buf.data()[AgentConfig.VALUES]
    dup1_vals = buf.get_duplicates()["dup1"].data()[AgentConfig.VALUES]
    dup2_vals = buf.get_duplicates()["dup2"].data()[AgentConfig.VALUES]
    assert main_vals == dup1_vals == dup2_vals == [100, 200]
    buf.clear()
    assert buf.size() == 0 and buf.get_duplicates()["dup1"].size() == 0 and buf.get_duplicates()["dup2"].size() == 0


def test_duplicate_ids_with_agent_store(agent: Agent):
    dup_a = TestBuffer(id="dupA", capacity=-1); dup_a.install(agent); agent.add_buffer(dup_a)
    dup_b = TestBuffer(id="dupB", capacity=-1); dup_b.install(agent); agent.add_buffer(dup_b)
    buf = TestBuffer(id="mainA", duplicate_ids=["dupA", "dupB"], capacity=-1)
    buf.install(agent)
    assert buf.get_duplicates()["dupA"] is dup_a
    assert buf.get_duplicates()["dupB"] is dup_b
    buf.push([7, 8, 9])
    assert dup_a.data()[AgentConfig.VALUES] == [7, 8, 9]
    assert dup_b.data()[AgentConfig.VALUES] == [7, 8, 9]


def test_data_persistent_false_all_clears():
    buf = TestBuffer(id="b6", capacity=-1)
    buf.install()
    buf.push([1, 2, 3])
    assert buf.size() == 3
    parsed_before = json.loads(buf.json())
    vals_before = parsed_before[AgentConfig.DATA][AgentConfig.VALUES][AgentConfig.VALUES]
    assert vals_before == [1, 2, 3]
    _ = buf.data(n=0, persistent=False)
    assert buf.size() == 0
