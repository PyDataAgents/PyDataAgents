import os
import time

from pydag.services.documents.RollingBackupService import DiscardMode, RollingBackupService
from pydag.services.ThreadType import ThreadType
from pydag.utils.FileUtils import FileUtils

def test_010():
    sf : str = os.path.dirname(__file__) + os.sep + "Mappe1.xlsx"
    tf : str = os.path.dirname(__file__) + os.sep + "test_backup"
    s = RollingBackupService(thread_type=ThreadType.SECOND.value,
                             observing_time=1,
                             source=sf,
                             target=tf,
                             discard_mode=DiscardMode.OLDEST.value,
                             max_backups=4,
                             zipped = True
                             )
    s.install()
    
    s.start()
    
    time.sleep(8)
    
    s.stop()
    
    s.uninstall()
    
    assert len(FileUtils.list_files(os.path.dirname(__file__) + os.sep)), s.max_backups
    
def test_011():
    sf : str = os.path.dirname(__file__) + os.sep + "Mappe1.xlsx"
    tf : str = os.path.dirname(__file__) + os.sep + "test_backup"
    s = RollingBackupService(thread_type=ThreadType.SECOND.value,
                             observing_time=1,
                             source=sf,
                             target=tf,
                             discard_mode=DiscardMode.EQUIDISTANT.value,
                             max_backups=5,
                             zipped = True
                             )
    s.install()
    
    s.start()
    
    time.sleep(60)
    
    s.stop()
    
    s.uninstall()
    
    assert len(FileUtils.list_files(os.path.dirname(__file__) + os.sep)), s.max_backups