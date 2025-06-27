from pathlib import Path
from pydatagrabber.utils.FileUtils import FileUtils


def test_000():
    
    files = FileUtils.list_files(Path.home() / "Downloads")
    
    print(files)
    
def test_010():
    files = FileUtils.list_files(Path.home() / "Downloads", pattern = "GUI")
    print(files)
    
def test_020():
    files = FileUtils.list_files(Path.home() / "Downloads", extension = "exe")
    print(files)
    
def test_030():
    files = FileUtils.list_files(Path.home() / "Downloads", newer_than_seconds=300)
    print(files)
    
def test_040():
    bytes = FileUtils.get_folder_bytes(Path.home() / "Downloads")
    print(bytes)
    
def test_050():
    files = FileUtils.list_files(Path.home() / "Downloads")
    file_extensions = list(f.split('.')[-1] for f in files if '.' in f)
    print(file_extensions)
    file_extensions = FileUtils.get_extensions_from_folder(Path.home() / "Downloads")
    print(file_extensions)