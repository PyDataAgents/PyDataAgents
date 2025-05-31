from PyDataGrabber.pydatagrabber.utils.FileUtils import FileUtils


def test_000():
    
    files = FileUtils.list_files("C:\\Users\\hille\\Downloads")
    
    print(files)
    
def test_010():
    files = FileUtils.list_files("C:\\Users\\hille\\Downloads", pattern = "GUI")
    print(files)
    
def test_020():
    files = FileUtils.list_files("C:\\Users\\hille\\Downloads", extension = "exe")
    print(files)
    
def test_030():
    files = FileUtils.list_files("C:\\Users\\hille\\Downloads", newer_than_seconds=300)
    print(files)