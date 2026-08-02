from pydag.agents.AgentKeywords import AgentKeywords
from pydag.buffers.DatasetBuffer import DatasetBuffer


def test_000():
    db = DatasetBuffer(dataset_name="ArrowHead", duplicate_ids=["DB1"], capacity=AgentKeywords.INFINITE_CAPACITY)
    db.install()
    db1 = db._duplicates["DB1"]
    
    n = 10
    print(db1.data(n=n, persistent=False))
    print(db.size())
    print(db1.size())
    assert db.size() - n == db1.size(), "duplicate DatasetBuffer does not have correct size after data() call"

def test_001():
    signal_2 = DatasetBuffer(id="signal_2", dataset_name="CWRU", sort_by_y=True, index_enabled=False)
    signal_2.install()
    assert all(isinstance(val, list) for val in signal_2._elements.values()) # All values are lists
    assert len(set(len(val) for val in signal_2._elements.values())) == 1 # All lists have the same length
    assert "index" not in signal_2._elements and "timestamps" not in signal_2._elements

def test_002():
    # Assert that a index column is created but no timestamp column. Use car data.
    signal_2 = DatasetBuffer(id="signal_2", dataset_name="Car", sort_by_y=True, index_enabled=True)
    signal_2.install()
    assert all(isinstance(val, list) for val in signal_2._elements.values()) # All values are lists
    assert len(set(len(val) for val in signal_2._elements.values())) == 1 # All lists have the same length
    assert "index" in signal_2._elements and "timestamps" not in signal_2._elements # index but not timestamp

def test_003():
    # Assert that a timestamp column is created but no index column. Use Ford A data.
    signal_2 = DatasetBuffer(id="signal_2", dataset_name="FordA", sort_by_y=True, timestamps_enabled=True)
    signal_2.install()
    assert all(isinstance(val, list) for val in signal_2._elements.values()) # All values are lists
    assert len(set(len(val) for val in signal_2._elements.values())) == 1 # All lists have the same length
    assert "index" not in signal_2._elements and "timestamps" in signal_2._elements # index but not timestamp


def test_004():
    # Assert that both, an index and a timestamp column are creted with the specified names. Use Blobs data. 
    signal_2 = DatasetBuffer(id="signal_2", dataset_name="Blobs", sort_by_y=True, index_enabled=True, timestamps_enabled=True, index_key="my_custom_index", timestamps_key="my_custom_timestamp")
    signal_2.install()
    assert all(isinstance(val, list) for val in signal_2._elements.values()) # All values are lists
    assert len(set(len(val) for val in signal_2._elements.values())) == 1 # All lists have the same length
    assert "my_custom_index" in signal_2._elements and "my_custom_timestamp" in signal_2._elements # custom index and timestamp

