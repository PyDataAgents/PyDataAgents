import pytest

from pydag.nodes.NodeException import NodeException
from pydag.utils.NodeUtils import NodeUtils

DATA = {
    "temperature": [20.1, 20.2],
    "pressure": [1.0, 1.1],
    "active": [True, False],
    "status": ["ok", "warn"],
}


def test_validate_key_names_rejects_non_list_input():
    with pytest.raises(NodeException, match="input_keys must be a list or tuple"):
        NodeUtils.validate_key_names("input_keys", "values")


def test_validate_key_names_rejects_duplicate_entries():
    with pytest.raises(NodeException, match="output_keys must contain unique entries"):
        NodeUtils.validate_key_names("output_keys", ["a", "a"])


def test_validate_key_names_rejects_unknown_type_selector():
    with pytest.raises(NodeException, match="supports only type:string and type:number"):
        NodeUtils.validate_key_names("input_keys", ["type:uuid"], allow_special=True)


def test_filter_data_by_selectors_supports_exact_names():
    assert NodeUtils.filter_data_by_selectors(DATA, ["pressure"]) == {
        "pressure": [1.0, 1.1]
    }


def test_filter_data_by_selectors_supports_slice_strings():
    assert NodeUtils.filter_data_by_selectors(DATA, ["1:3"]) == {
        "pressure": [1.0, 1.1],
        "active": [True, False],
    }


def test_filter_data_by_selectors_supports_type_string():
    assert NodeUtils.filter_data_by_selectors(DATA, ["type:string"]) == {
        "status": ["ok", "warn"]
    }


def test_filter_data_by_selectors_supports_type_number_with_bool():
    assert NodeUtils.filter_data_by_selectors(DATA, ["type:number"]) == {
        "temperature": [20.1, 20.2],
        "pressure": [1.0, 1.1],
        "active": [True, False],
    }


def test_filter_data_by_selectors_applies_selectors_with_or_semantics():
    assert NodeUtils.filter_data_by_selectors(DATA, ["2:4", "type:string"]) == {
        "active": [True, False],
        "status": ["ok", "warn"],
    }
