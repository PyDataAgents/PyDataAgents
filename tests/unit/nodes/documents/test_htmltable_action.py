import os
import webbrowser

from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.HTMLFileAction import HTMLFileAction
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
    
def test_010():
    
    buf = DictBuffer()
    buf.install()
    
    buf.push({"A": [1,2,3], "B": ["z", "zz", None]})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    hta = HTMLTableAction()
    hta.add_parent(lba)
    hta.install()    
    hta.execute()
    
    html_file = os.path.dirname(__file__) + os.sep + "test_010.html"
    hfa = HTMLFileAction(path=html_file)
    hfa.add_parent(hta)
    hfa.install()
    hfa.execute()
    
    webbrowser.open(html_file)