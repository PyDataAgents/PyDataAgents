from pathlib import Path
import time
from pydag.services.documents.FileWatchdogService import FileWatchdogService


def test_000():
    service = FileWatchdogService()
    service.folders = [Path.home() / "Downloads"]
    service.install()
    service.start()
    
    time.sleep(3)
    
    service.stop()