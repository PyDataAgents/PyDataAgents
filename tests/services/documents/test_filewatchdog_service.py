from pathlib import Path
import time
from pydg.services.documents.FileWatchdogService import FileWatchdogService


def test_000():
    service = FileWatchdogService()
    service.folders = [Path.home() / "Downloads"]
    
    service.start()
    
    time.sleep(120)
    
    service.stop()