from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.HTMLTableAction import HTMLTableAction


def test_000():
    
    buf = DictBuffer()
    buf.install()
    
    buf.push({"A": [1,2,3]})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    hta = HTMLTableAction()
    hta.add_parent(lba)
    hta.install()    
    hta.execute()
    
    data = hta.get_buffer().data()
    print(data)
    