import pytest

from pydag.agents.AgentConfig import AgentConfig
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.BufferNode import BufferNode
from pydag.nodes.NodeException import NodeException
from pydag.nodes.documents.ReadCsvAction import ReadCsvAction


def test_000():

    s = "".join(filter(str.isupper, BufferNode.cname())) + f"-{AgentConfig.FEATURE}" + "-{i}"
    print(s)

    ss = s.format(i=1)

    print(ss)
    

def test_validate_key_names_rejects_non_list_input():
    with pytest.raises(NodeException, match="must be a list or tuple"):
        rca = ReadCsvAction(input_keys="values")
        rca.install()
        
def test_validate_key_names_empty_string():
    with pytest.raises(NodeException, match="must contain only non-empty strings"):
        rca = ReadCsvAction(input_keys=[""])
        rca.install()


def test_validate_key_names_rejects_duplicate_entries():
    with pytest.raises(NodeException, match="must contain unique entries"):
        rca = ReadCsvAction(output_keys=["values", "values "])
        rca.install()


def test_get_parent_data_supports_slice_and_type_selectors():
    parent = BufferNode()
    parent.set_buffer(DictBuffer())
    parent.get_buffer().install()
    parent.get_buffer().push(
        {
            "temperature": [20.0, 21.0],
            "pressure": [1.0, 1.1],
            "active": [True, False],
            "status": ["ok", "warn"],
        }
    )

    node = BufferNode(input_keys=["1:3", "type:string"], input_selector_mode=True)
    node.add_parent(parent)
    node.install()

    assert node.get_parent_data() == {
        "pressure": [1.0, 1.1],
        "active": [True, False],
        "status": ["ok", "warn"],
    }
