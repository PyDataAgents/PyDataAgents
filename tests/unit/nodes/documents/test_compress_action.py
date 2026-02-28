import os
from pydag.nodes.documents.CompressAction import CompressAction
from pydag.nodes.documents.DecompressAction import DecompressAction
from pydag.utils.FileUtils import FileUtils


def test_compress_action():
    source_file = os.path.dirname(__file__) + os.sep + "plotly_test_000.html"
    ca = CompressAction(source_file=source_file, target_file=None)
    ca.install()
    ca.execute()
    
    zip_file = os.path.dirname(__file__) + os.sep + "plotly_test_000.zip"
    
    assert FileUtils.exists_file(zip_file), "no test.zip was created"
    
def test_decompress_action():
    source_file = os.path.dirname(__file__) + os.sep + "plotly_test_000.zip"
    target_dir = os.path.dirname(__file__) + os.sep + "test_decompressed"
    ca = DecompressAction(source_file=source_file, target_dir=target_dir)
    ca.install()
    ca.execute()
    
    assert FileUtils.exists_folder(target_dir), "no test_deompressed folder was created"