from pathlib import Path
import time
from pydatagrabber.buffers.DataType import DataType
from pydatagrabber.buffers.ListBuffer import ListBuffer
from pydatagrabber.statemachine.StatemachineService import StatemachineService
from pydatagrabber.statemachine.actions.ListFilesAction import ListFilesAction
from pydatagrabber.statemachine.actions.MoveFilesAction import MoveFilesAction
from pydatagrabber.statemachine.actions.SleepAction import SleepAction


def test000():
    
    buf = ListBuffer()
    buf.id = "FILES"
    buf.capacity = 10000
    buf.data_type = DataType.STRING.value
    buf.description = "buffer to store files from directory listing"
    
    la = ListFilesAction()
    la.buffer = buf
    la.folder = str(Path.home() / "Downloads" / "t")
    
    ma = MoveFilesAction()
    ma.buffer = buf
    ma.target_folder = str(Path.home() / "Downloads" / "tt")
    
    sa = SleepAction()
    sa.sleep_time = 20
    
    la.add_child(ma)
    ma.add_child(sa)    
    
    sm = StatemachineService()
    sm.add_node(la)
    sm.add_node(ma)
    sm.add_node(sa)
    sm.start_action = la
    
    sm.start()
    
    while True:
        time.sleep(3)
    