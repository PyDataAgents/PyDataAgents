import os

from pydag.nodes.documents.ListFilesAction import ListFilesAction


def test_000():
    
    folder = os.path.dirname(__file__)
    lfa = ListFilesAction(folder=folder)
    lfa.install()
    lfa.execute()
    print(lfa.get_buffer().data())
    
    
def test_010():
    
    folder = os.path.dirname(__file__)
    lfa = ListFilesAction(folder=folder, extension=".py")
    lfa.install()
    lfa.execute()
    print(lfa.get_buffer().data())