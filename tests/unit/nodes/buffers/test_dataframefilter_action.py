import pytest

from pydag.agents.AgentElementException import AgentElementException
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.DataFrameFilterAction import DataFrameFilterAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction


def test_dataframefilter_row_filter():
    # Create a sample DataFrame
    data = {
        'A': [1, 2, 3, 4, 5],
        'B': ['x', 'y', 'z', 'x', 'y']
    }

    buf = DictBuffer()
    buf.install()
    
    buf.push(data)
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()

    # Create a DataFrameFilterAction instance
    dfa = DataFrameFilterAction(row_filter="A > 2")
    dfa.add_parent(lba)
    dfa.install()
    dfa.execute()
    
    # Get the filtered data
    filtered_data = dfa.get_buffer().data()
    
    # Check if the filtered data is correct
    assert len(next(iter(filtered_data.values()))) == 3
    assert all(value > 2 for value in next(iter(filtered_data.values())))
    
def test_dataframefilter_column_filter():
    # Create a sample DataFrame
    data = {
        'A': [1, 2, 3, 4, 5],
        'B': ['x', 'y', 'z', 'x', 'y'],
        'C': [10, 20, 30, 40, 50]
    }

    buf = DictBuffer()
    buf.install()
    
    buf.push(data)
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()

    # Create a DataFrameFilterAction instance
    dfa = DataFrameFilterAction(row_filter="A > 2", column_filter=["B", "C"])
    dfa.add_parent(lba)
    dfa.install()
    dfa.execute()
    
    # Get the filtered data
    filtered_data = dfa.get_buffer().data()
    
    # Check if the filtered data is correct
    assert len(next(iter(filtered_data.values()))) == 3
    assert set(filtered_data.keys()) == {"B", "C"}
    
def test_install_exception():
    # Create a DataFrameFilterAction instance without specifying row_filter or column_filter
    dfa = DataFrameFilterAction()
    
    with pytest.raises(AgentElementException) as exc_info:
        print(exc_info)
        dfa.install()
    