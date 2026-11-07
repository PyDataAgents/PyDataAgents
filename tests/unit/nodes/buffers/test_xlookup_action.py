import pytest

from pydag.agents.AgentElementException import AgentElementException
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.buffers.XLookupAction import XLookupAction
from pydag.utils.DataUtils import DataUtils


def test_xlookup_returns_first_exact_match_and_configured_fallback():
   
    data=[
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 35},
        {"id": 4, "name": "Alice", "age": 28},  # Duplicate name
    ]
    
    parent_buffer = DictBuffer(index_enabled=False, timestamps_enabled=False)
    parent_buffer.install()
    parent_buffer.push(data)

    lba = LinkBufferAction()
    lba.set_buffer(parent_buffer)
    lba.install()
    
    xlookup_action = XLookupAction(
        lookup_values=["Alice", "Charlie", "Eve"],
        lookup_column="name",
        return_column="age",
        not_found_value=0,
    )
    
    xlookup_action.add_parent(lba)
    xlookup_action.install()
    
    xlookup_action.execute()

    expected_result = [
        {"age": 30},  # First match for Alice
        {"age": 35},  # Match for Bob
        {"age": 0},   # No match for Eve
    ]

    data = DataUtils.dict_to_list(xlookup_action.get_data())
        
    assert data == expected_result
    
def test_missing_properties():
    xlookup_action = XLookupAction(
        lookup_values=["Alice", "Charlie", "Eve"],
        lookup_column=None,  # Missing lookup_column
        return_column="age",
        not_found_value=0,
    )
    
    with pytest.raises(AgentElementException):
        xlookup_action.install()
    
    xlookup_action = XLookupAction(
        lookup_values=["Alice", "Charlie", "Eve"],
        lookup_column="name",
        return_column=None,  # Missing return_column
        not_found_value=0,
    )
    
    with pytest.raises(AgentElementException):
        xlookup_action.install()
    
    xlookup_action = XLookupAction(
        lookup_values=[],  # Empty lookup_values
        lookup_column="name",
        return_column="age",
        not_found_value=0,
    )
    
    with pytest.raises(AgentElementException):
        xlookup_action.install()
