import os
from pathlib import Path

from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.WriteJsonAction import WriteJsonAction


def test_write_json_action():
    buf = DictBuffer()
    buf.install()
    buf.push({"a": 1, "b": "s"})
    buf.push({"a": 2, "b": "t"})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    
    file_path = os.path.dirname(__file__) + os.sep + "test_write.json"
    wa = WriteJsonAction(file_path=file_path)
    wa.add_parent(lba)
    wa.install()    
    wa.execute()
    
    assert Path(file_path).exists()
    
def test_write_json_action2():
    buf = DictBuffer()
    buf.install()
    buf.push({"fp": "","a": 1, "b": "s"})
    buf.push({"fp": "","a": 2, "b": "t"})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    
    file_path = os.path.dirname(__file__) + os.sep + "test_write.json"
    wa = WriteJsonAction(file_path=file_path)
    wa.add_parent(lba)
    wa.install()    
    wa.execute()
    
    assert Path(file_path).exists()