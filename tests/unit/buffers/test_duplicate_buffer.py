from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.ListBuffer import ListBuffer
from pydag.buffers.TimedBuffer import TimedBuffer
from pydag.agents.Agent import Agent
from pydag.buffers.DatasetBuffer import DatasetBuffer


def test_000():
    
    b1 = DictBuffer()
    b1.install()
    b2 = DictBuffer()
    b2.install()
    
    db = DictBuffer(id="DB", duplicate_ids=["B1", "B2", "B3"])
    db._duplicates[b1.id] = b1
    db._duplicates[b2.id] = b2
    db.install()
    
    print(db.duplicate_ids)
    
def test_010():
    
    db = DictBuffer(id="DB", duplicate_ids=["B1", "B2", "B3"])
    db.install()
    
    print(db.duplicate_ids)
    
    for buf in db._duplicates.values():
        print(buf.config_options())
        
def test_020():
    db = DictBuffer(id="DB", duplicate_ids=["B1", "B2"], capacity=1)
    db.install()
    
    db.push({"A": 1.0})
    
    d1 = db._duplicates["B1"].data()
    d2 = db._duplicates["B2"].data()
    
    assert d1 == d2, "duplicate buffers do not contain same data"
        
    
def test_021():
    db = DictBuffer(id="DB", duplicate_ids=["B1", "B2"], capacity=1)
    db.install()
    
    db.push({"A": 1.0})
    
    d1 = db._duplicates["B1"].data()
    d2 = db._duplicates["B2"].data()
    
    db.clear()
    
    assert db.size() == 0 and db._duplicates["B1"].size() == 0 and db._duplicates["B2"].size() == 0, "buffers not cleared properly"
  
    
    
def test_030():
    lbuf = ListBuffer(id="LB", capacity=5, duplicate_ids=["LB1", "LB2"])
    lbuf.install()
    
    lbuf.push([1,2,3])
    
    lbuf1 = lbuf._duplicates["LB1"]
    
    assert lbuf1 is not None, "duplicate ListBuffer LB1 does not exist"
    assert lbuf1.size() == 3, "duplicate ListBuffer does not contain correct number of elements"
    
    
def test_031():
    lbuf = ListBuffer(id="LB", capacity=5, duplicate_ids=["LB1", "LB2"])
    lbuf.install()
    
    lbuf.push([1,2,3])
    
    lbuf1 = lbuf._duplicates["LB1"]
    lbuf2 = lbuf._duplicates["LB2"]
    
    d1 = lbuf1.data(n=2, persistent=False)
    print(d1)
    
    assert lbuf1.size() == 1 and lbuf2.size() == 3 and lbuf.size() == 3, "duplicate ListBuffers do not have correct size after data() call"
        
def test_040():
    tbuf = TimedBuffer(id="TB", capacity=5, duplicate_ids=["TB1", "TB2"])
    tbuf.install()
    
    tbuf.push([10,20,30])
    
    tbuf1 = tbuf._duplicates["TB1"]
    tbuf2 = tbuf._duplicates["TB2"]
    
    print(tbuf.data())
    print(tbuf1.data())
    
    assert tbuf1.size() == 3 and tbuf2.size() == 3, "duplicate TimedBuffers do not have correct size after data() call"


def test_duplicate_dataset_buffer():
    ag = Agent()

    buf1 = DatasetBuffer(id="DATASET_BUF_1", dataset_name="ArrowHead", duplicate_ids = ["DATASET_BUF_2", "DATASET_BUF_3"])
    buf1.install()
    ag.add_buffer(buf1)
    ag.add_buffer(buf1._duplicates["DATASET_BUF_2"])
    ag.add_buffer(buf1._duplicates["DATASET_BUF_3"])
    
    ag.install()

    
    

    bs = ag._buffer_store

    # assert that the values in all three buffers are the same
    data1 = bs["DATASET_BUF_1"].data()
    data2 = bs["DATASET_BUF_2"].data()
    data3 = bs["DATASET_BUF_3"].data()
    assert data1 == data2 == data3, "Duplicate DatasetBuffers do not contain the same data"

