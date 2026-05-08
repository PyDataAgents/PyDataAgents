import pytest

from pydag.nodes.NodeException import NodeException
from pydag.nodes.BufferNode import BufferNode

DATA = {
    "temperature": [20.1, 20.2],
    "pressure": [1.0, 1.1],
    "active": [True, False],
    "status": ["ok", "warn"],
}


def test_validate_key_names_rejects_non_uniform_string_input():
    with pytest.raises(NodeException, match="keys must contain only non-empty strings"):
        BufferNode._validate_keys(["a", 1])
        
        
def test_validate_key_names_rejects_non_uniform_int_input():
    with pytest.raises(NodeException, match="keys must contain all integer entries"):
        BufferNode._validate_keys([1, "a"])


def test_validate_key_names_rejects_duplicate_entries():
    with pytest.raises(NodeException, match="keys must contain unique entries"):
        BufferNode._validate_keys(["a", "a"])


def test_validate_key_names_rejects_unknown_type_selector():
    with pytest.raises(NodeException, match="supports only type:string and type:number"):
        BufferNode._validate_keys(["type:uuid"])

