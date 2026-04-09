import pytest

from pydag.agents.AgentConfig import AgentConfig
from pydag.nodes.BufferNode import BufferNode
from pydag.nodes.NodeException import NodeException
from pydag.nodes.documents.ReadCsvAction import ReadCsvAction


def test_000():

    s = "".join(filter(str.isupper, BufferNode.cname())) + f"-{AgentConfig.FEATURE}" + "-{i}"
    print(s)

    ss = s.format(i=1)

    print(ss)
    

def test_validate_key_names_rejects_non_list_input():
    with pytest.raises(NodeException, match="must be of type list"):
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
