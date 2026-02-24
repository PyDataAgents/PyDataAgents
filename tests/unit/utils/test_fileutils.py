import os
import shutil
from pathlib import Path
from pydag.utils.FileUtils import FileUtils


def test_000():    
    files = FileUtils.list_files(Path.home() / "Downloads")    
    print(files)
    
def test_001():    
    files = FileUtils.list_files(Path.home() / "Downloads", recursive=True)
    print(files)
    
def test_010():
    files = FileUtils.list_files(Path.home() / "Downloads", pattern = "GUI")
    print(files)
    
def test_020():
    files = FileUtils.list_files(Path.home() / "Downloads", extension = "exe")
    print(files)

def test_021_list_extension_multiple():
    # Create temporary folder and files
    tmp = Path(os.path.dirname(__file__)) / "tmp_list_files_ext"
    FileUtils.create_dir(str(tmp))
    (tmp / "a.txt").write_text("a")
    (tmp / "b.exe").write_text("b")
    (tmp / "c.pdf").write_text("c")

    files = FileUtils.list_files(str(tmp), extension=["exe", "txt"])
    print(files)
    assert files is not None
    assert any(f.endswith("exe") for f in files)
    assert any(f.endswith("txt") for f in files)
    assert not any(f.endswith("pdf") for f in files)

    # Cleanup
    shutil.rmtree(tmp)

def test_022_list_extension_single():
    # Create temporary folder and files
    tmp = Path(os.path.dirname(__file__)) / "tmp_list_files_ext_single"
    FileUtils.create_dir(str(tmp))
    (tmp / "a.txt").write_text("a")
    (tmp / "b.exe").write_text("b")
    (tmp / "c.pdf").write_text("c")

    files = FileUtils.list_files(str(tmp), extension="txt")
    print(files)
    assert files is not None
    assert any("a.txt" in f for f in files)
    assert not any("b.exe" in f for f in files)
    assert not any("c.pdf" in f for f in files)

    # Cleanup
    shutil.rmtree(tmp)
    
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

def test_011_list_pattern_multiple():
    # Create temporary folder and files
    tmp = Path(os.path.dirname(__file__)) / "tmp_list_files_pattern"
    FileUtils.create_dir(str(tmp))
    (tmp / "alpha.txt").write_text("alpha")
    (tmp / "GUI_manual.pdf").write_text("content")
    (tmp / "notes_MANUAL.doc").write_text("content")

    files = FileUtils.list_files(str(tmp), pattern=["GUI", "MANUAL"])
    print(files)
    assert files is not None
    assert any("GUI_manual.pdf" in f for f in files)
    assert any("notes_MANUAL.doc" in f for f in files)
    assert not any("alpha.txt" in f for f in files)

    # Cleanup
    shutil.rmtree(tmp)

def test_012_list_pattern_single():
    # Create temporary folder and files
    tmp = Path(os.path.dirname(__file__)) / "tmp_list_files_pattern_single"
    FileUtils.create_dir(str(tmp))
    (tmp / "alpha.txt").write_text("alpha")
    (tmp / "GUI_manual.pdf").write_text("content")
    (tmp / "notes_MANUAL.doc").write_text("content")

    files = FileUtils.list_files(str(tmp), pattern="GUI")
    print(files)
    assert files is not None
    assert any("GUI_manual.pdf" in f for f in files)
    assert not any("notes_MANUAL.doc" in f for f in files)
    assert not any("alpha.txt" in f for f in files)

    # Cleanup
    shutil.rmtree(tmp)
    
def test_060():
    folder = Path.home() / "Downloads" / "testfolder"
    FileUtils.create_dir(str(folder))
    
def test_061():
    file_path = Path.home() / "Downloads" / "testfolder2" / "test.txt"
    FileUtils.create_dir(str(file_path))
    
def test_compress_file():    
    source_file = os.path.dirname(__file__) + os.sep + "test_table.html"
    p = FileUtils.compress(source_file)
    print(p)
    
def test_compress_file_to_target():
    source_file = os.path.dirname(__file__) + os.sep + "test_table.html"
    target_file = os.path.dirname(__file__) + os.sep + "test.zip"
    p = FileUtils.compress(source_file, target_file)
    print(p)
    
def test_compress_folder():
    source_folder = os.path.dirname(__file__) + os.sep + "__pycache__"
    p = FileUtils.compress(source_folder)
    print(p)    

def test_compress_folder_to_target():
    source_folder = os.path.dirname(__file__) + os.sep + "__pycache__"
    target_folder = Path.home() / "Downloads" / "__pycache__"
    p = FileUtils.compress(source_folder, target_file=target_folder)
    print(p)
    
def test_decompress_file():
    source_file = os.path.dirname(__file__) + os.sep + "test_table.zip"
    p = FileUtils.decompress(source_file)
    print(p)
    
def test_decompress_file_to_target():
    source_file = os.path.dirname(__file__) + os.sep + "__pycache__.zip"
    target_dir = Path.home() / "Downloads" / "__pycache__"
    p = FileUtils.decompress(source_file, target_dir)
    print(p)
      
