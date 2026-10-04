import os

from pydag.nodes.documents.CopyFilesAction import CopyFilesAction
from pydag.nodes.documents.ListFilesAction import ListFilesAction
from pydag.utils.FileUtils import FileUtils


def test_copy_files():
    folder = os.path.dirname(__file__)
    la = ListFilesAction(folder=folder)
    la.install()
    
    tfolder = FileUtils.user_home() + os.sep + "Downloads" + os.sep + "test_copy_files"
    ca = CopyFilesAction(target_folder=tfolder)
    ca.add_parent(la)
    ca.install()
    
    la.execute()
    ca.execute()
    
    assert len(FileUtils.list_files(tfolder)) > 0
    FileUtils.delete_dir(tfolder)