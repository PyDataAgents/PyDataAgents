import os
import time
import webbrowser
from pydag.services.documents.HttpFileService import HttpFileService


def test_000():
    
    folder = os.path.dirname(__file__)
    fhs = HttpFileService(folder_path=folder, port=8098)
    
    fhs.install()
    fhs.start()
    
    time.sleep(2)
    
    webbrowser.open(f"https://3dviewer.net/#model=http://localhost:{fhs.port}/plate.step")
    
    time.sleep(5)