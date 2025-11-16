from pydag.buffers.BufferException import BufferException
from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.DuplicateBuffer import DuplicateBuffer


def test_000():
    
    b1 = DictBuffer()
    b1.install()
    b2 = DictBuffer()
    b2.install()
    
    db = DuplicateBuffer(id="DB", duplicate_ids=["B1", "B2", "B3"])
    db.duplicates[b1.id] = b1
    db.duplicates[b2.id] = b2
    db.install()
    
    print(db.duplicate_ids)
    
def test_010():
    
    db = DuplicateBuffer(id="DB", duplicate_ids=["B1", "B2", "B3"])
    db.install()
    
    print(db.duplicate_ids)
    
    for buf in db.duplicates.values():
        print(buf.config_options())
        
def test_020():
    db = DuplicateBuffer(id="DB", duplicate_ids=["B1", "B2"], capacity=1)
    db.install()
    
    db.push({"A": 1.0})
    
    d1 = db.duplicates["B1"].data()
    d2 = db.duplicates["B2"].data()
    
    if d1 == d2:
        assert True
    else:
        raise BufferException("duplicates do not contain same data")
    
def test_021():
    db = DuplicateBuffer(id="DB", duplicate_ids=["B1", "B2"], capacity=1)
    db.install()
    
    db.push({"A": 1.0})
    
    d1 = db.duplicates["B1"].data()
    d2 = db.duplicates["B2"].data()
    
    db.clear()
    
    if db.size() == 0 and db.duplicates["B1"].size() == 0 and db.duplicates["B2"].size() == 0:
        assert True
    else:
        raise BufferException("duplicate buffers have not been cleared properly")