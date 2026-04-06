import os
import webbrowser

from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.HTMLFileAction import HTMLFileAction
from pydag.utils.FileUtils import FileUtils


def test_path_as_file():
    buf = DictBuffer()
    buf.install()
    buf.push({"html": "<div>Hello World!</div>"})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    html_file = os.path.dirname(__file__) + os.sep + "test_file.html"    
    hfa = HTMLFileAction(path=html_file)    
    hfa.add_parent(lba)
    hfa.install()    
    hfa.execute()
    
    webbrowser.open(html_file)
    
def test_path_as_folder():
    buf = DictBuffer()
    buf.install()
    buf.push({"html": "<div>Hello World!</div>"})
    buf.push({"html": "<div>Hello World2!</div>"})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    html_file = os.path.dirname(__file__)    
    hfa = HTMLFileAction(path=html_file)
    hfa.add_parent(lba)
    hfa.install()    
    hfa.execute()
    
    data = hfa.get_buffer().data()
    for k, values in data.items():
        for v in values:
            if isinstance(v, str):
                FileUtils.delete_file(v)