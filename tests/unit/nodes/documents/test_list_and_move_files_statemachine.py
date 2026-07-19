from pathlib import Path
import time
from pydag.buffers.DataType import DataType
from pydag.buffers.ListBuffer import ListBuffer
from pydag.services.statemachine.SimpleStatemachine import SimpleStatemachine
from pydag.nodes.documents.ListFilesAction import ListFilesAction
from pydag.nodes.documents.MoveFilesAction import MoveFilesAction
from pydag.nodes.utils.SleepAction import SleepAction
from pydag.utils.FileUtils import FileUtils


def test000():
    
    buf = ListBuffer()
    buf.id = "FILES"
    buf.capacity = 10000
    buf.data_type = DataType.STRING.value
    buf.description = "buffer to store files from directory listing"
    
    f1 = str(Path.home() / "Downloads" / "t")
    f2 = str(Path.home() / "Downloads" / "tt")
    FileUtils.create_dir(f1)
    FileUtils.create_dir(f2)
    
    la = ListFilesAction()
    la.set_buffer(buf)
    la.folder = f1
    
    ma = MoveFilesAction()
    ma.set_buffer(buf)
    ma.target_folder = f2
    
    sa = SleepAction()
    sa.sleep_time = 3
    
    la.add_child(ma)
    ma.add_child(sa)    
    
    sm = SimpleStatemachine()
    sm.install()
    sm.add_node(la)
    sm.add_node(ma)
    sm.add_node(sa)
    
    sm.start()
    
    time.sleep(10)
    
    sm.stop()
    