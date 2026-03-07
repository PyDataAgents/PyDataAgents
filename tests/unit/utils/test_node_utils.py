import pytest

from pydag.nodes.NodeException import NodeException
from pydag.utils.NodeUtils import NodeUtils


def test_validate_key_names_rejects_non_list_input():
    with pytest.raises(NodeException, match="input_keys must be a list or tuple"):
        NodeUtils.validate_key_names("input_keys", "values")


def test_validate_key_names_rejects_duplicate_entries():
    with pytest.raises(NodeException, match="output_keys must contain unique entries"):
        NodeUtils.validate_key_names("output_keys", ["a", "a"])
