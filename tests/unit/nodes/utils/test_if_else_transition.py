import pytest

from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.NodeException import NodeException
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.utils.IfTransition import IfTransition
from pydag.nodes.utils.PrintBufferAction import PrintBufferAction

def test_if_condition1():
    buf = DictBuffer(index_enabled=False, timestamps_enabled=False)
    buf.install()
    
    buf.push({"d": [1.0, 2.1, 3.5, -1.0]})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    ex : str = """
        data.d > 1.0
    """
    
    it = IfTransition(expression=ex)
    it.add_parent(lba)
    it.install()
    
    pa = PrintBufferAction()
    pa.add_parent(it)
    pa.install()
    
    lba.execute()
    if it.check():
        assert len(it.get_buffer().data()["d"]) == 2
        pa.execute()
        
def test_if_condition2():
    buf = DictBuffer(index_enabled=False, timestamps_enabled=False)
    buf.install()
    
    buf.push({"d": [1.0, 2.1, 3.5, -1.0], "b": [True, False, True, False]})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    ex : str = """
        data.d > 1.0 && data.b
    """
    
    it = IfTransition(expression=ex)
    it.add_parent(lba)
    it.install()
    
    pa = PrintBufferAction()
    pa.add_parent(it)
    pa.install()
    
    lba.execute()
    if it.check():
        assert len(it.get_data(by_rows=True)) == 1
        pa.execute()
        
def test_if_condition3():
    buf = DictBuffer(index_enabled=False, timestamps_enabled=False)
    buf.install()
    
    buf.push({"d": [1.0, 2.1, 3.5, -1.0], "b": [True, False, True, False]})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    ex : str = """
        obj.d > 1.0 && data.c
    """
    
    it = IfTransition(expression=ex)
    it.add_parent(lba)
    it.install()
    
    pa = PrintBufferAction()
    pa.add_parent(it)
    pa.install()
    
    lba.execute()
    with pytest.raises(NodeException):
        if it.check():
            assert len(it.get_data(by_rows=True)) == 1
            pa.execute()   
