import time
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.DatasetBuffer import DatasetBuffer


def test_000():
    signal_2 = DatasetBuffer(id="signal_2", dataset_name="CWRU", sort_by_y=True, index_enabled=False)
    signal_2.install()
    assert all(isinstance(val, list) for val in signal_2.elements.values()) # All values are lists
    assert len(set(len(val) for val in signal_2.elements.values())) == 1 # All lists have the same length
    assert "index" not in signal_2.elements and "timestamps" not in signal_2.elements

def test_001():
    # Assert that a index column is created but no timestamp column. Use car data.
    signal_2 = DatasetBuffer(id="signal_2", dataset_name="Car", sort_by_y=True, index_enabled=True)
    signal_2.install()
    assert all(isinstance(val, list) for val in signal_2.elements.values()) # All values are lists
    assert len(set(len(val) for val in signal_2.elements.values())) == 1 # All lists have the same length
    assert "index" in signal_2.elements and "timestamps" not in signal_2.elements # index but not timestamp

def test_002():
    # Assert that a timestamp column is created but no index column. Use Ford A data.
    signal_2 = DatasetBuffer(id="signal_2", dataset_name="FordA", sort_by_y=True, timestamps_enabled=True)
    signal_2.install()
    assert all(isinstance(val, list) for val in signal_2.elements.values()) # All values are lists
    assert len(set(len(val) for val in signal_2.elements.values())) == 1 # All lists have the same length
    assert "index" not in signal_2.elements and "timestamps" in signal_2.elements # index but not timestamp


def test_003():
    # Assert that both, an index and a timestamp column are creted with the specified names. Use Blobs data. 
    signal_2 = DatasetBuffer(id="signal_2", dataset_name="Blobs", sort_by_y=True, index_enabled=True, timestamps_enabled=True, index_key="my_custom_index", timestamps_key="my_custom_timestamp")
    signal_2.install()
    assert all(isinstance(val, list) for val in signal_2.elements.values()) # All values are lists
    assert len(set(len(val) for val in signal_2.elements.values())) == 1 # All lists have the same length
    assert "my_custom_index" in signal_2.elements and "my_custom_timestamp" in signal_2.elements # custom index and timestamp

