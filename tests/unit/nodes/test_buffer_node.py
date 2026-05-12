import pytest

from pydag.agents.AgentConfig import AgentConfig
from pydag.agents.AgentElementException import AgentElementException
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.BufferNode import BufferNode
from pydag.nodes.NodeException import NodeException
from pydag.nodes.buffers.CopyDataAction import CopyDataAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.ReadCsvAction import ReadCsvAction

DATA = {
    "temperature": [20.1, 20.2],
    "pressure": [1.0, 1.1],
    "active": [True, False],
    "status": ["ok", "warn"],
}

def test_000():
    s = "".join(filter(str.isupper, BufferNode.cname())) + f"-{AgentConfig.FEATURE}" + "-{i}"
    print(s)
    ss = s.format(i=1)
    print(ss)    

def test_validate_key_names_rejects_non_list_input():
    rca = ReadCsvAction(input_keys="values")
    rca.install()
        
def test_validate_key_names_empty_string():
    with pytest.raises(AgentElementException):
        rca = ReadCsvAction(input_keys=[""])
        rca.install()


def test_validate_key_names_rejects_duplicate_entries():
    with pytest.raises(AgentElementException):
        rca = ReadCsvAction(output_keys=["values", "values "])
        rca.install()

def test_validate_key_names_rejects_non_uniform_string_input():
    with pytest.raises(NodeException, match="keys must contain only non-empty strings"):
        BufferNode._validate_keys(["a", 1])
        
        
def test_validate_key_names_rejects_non_uniform_int_input():
    with pytest.raises(NodeException, match="keys must contain all integer entries"):
        BufferNode._validate_keys([1, "a"])


def test_validate_key_names_rejects_duplicate_entries2():
    with pytest.raises(NodeException, match="keys must contain unique entries"):
        BufferNode._validate_keys(["a", "a"])


def test_validate_key_names_rejects_unknown_type_selector():
    with pytest.raises(NodeException):
        BufferNode._validate_keys("type:uuid")
        
def test_parse_keys_with_string_data():
    keys = BufferNode._parse_keys(list(DATA.keys()), "type:string", DATA)
    print(keys)
    assert "status" in keys, "wrong keys were parsed from sample DATA"
    
def test_parse_keys_with_number_data():
    keys = BufferNode._parse_keys(list(DATA.keys()), "type:number", DATA)
    print(keys)
    assert len(keys) == 3, "wrong keys were parsed from sample DATA"
    
def test_parse_keys_with_indices():
    keys = BufferNode._parse_keys(list(DATA.keys()), "0:3:2", DATA)
    print(keys)
    assert len(keys) == 2, "wrong keys were parsed from sample DATA"
    
def test_parse_keys_with_lastindex():
    keys = BufferNode._parse_keys(list(DATA.keys()), "-1", DATA)
    print(keys)
    assert len(keys) == 1, "wrong keys were parsed from sample DATA"

def test_parse_keys_with_last2index():
    keys = BufferNode._parse_keys(list(DATA.keys()), "-2:", DATA)
    print(keys)
    assert len(keys) == 2, "wrong keys were parsed from sample DATA"
    
def test_copy_data_with_list_int_input_keys():
    buf = DictBuffer()
    buf.install()
    buf.push(DATA)
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    buf2 = DictBuffer(index_enabled=False, timestamps_enabled=False)
    
    ca = CopyDataAction(input_keys=[1,3])
    ca.set_buffer(buf2)
    ca.add_parent(lba)
    ca.install()
    
    ca.execute()
    
    data = ca.get_buffer().data()
    assert len(data) == 2, "wrong number of keys extracted"
    
def test_copy_data_with_list_int_input_keys2():
    buf = DictBuffer()
    buf.install()
    buf.push(DATA)
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    buf2 = DictBuffer(index_enabled=False, timestamps_enabled=False)
    
    ca = CopyDataAction(input_keys=[1,3,100])
    ca.set_buffer(buf2)
    ca.add_parent(lba)
    ca.install()
    
    ca.execute()
    
    data = ca.get_buffer().data()
    assert len(data) == 2, "wrong number of keys extracted"
    
def test_copy_data_with_list_str_input_keys():
    buf = DictBuffer()
    buf.install()
    buf.push(DATA)
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    buf2 = DictBuffer(index_enabled=False, timestamps_enabled=False)
    
    ca = CopyDataAction(input_keys=["status", "pressure"])
    ca.set_buffer(buf2)
    ca.add_parent(lba)
    ca.install()
    
    ca.execute()
    
    data = ca.get_buffer().data()
    assert len(data) == 2, "wrong number of keys extracted"
    
 
def test_copy_data_with_str_slice():
    buf = DictBuffer()
    buf.install()
    buf.push(DATA)
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    buf2 = DictBuffer(index_enabled=False, timestamps_enabled=False)
    
    ca = CopyDataAction(input_keys=["status", "pressure"])
    ca.set_buffer(buf2)
    ca.add_parent(lba)
    ca.install()
    
    ca.execute()
    
    data = ca.get_buffer().data()
    assert len(data) == 2, "wrong number of keys extracted"    