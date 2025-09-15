import os

from pydag.statemachine.actions.documents.ListFilesAction import ListFilesAction


def test_000():
    
    folder = os.path.dirname(__file__)
    lfa = ListFilesAction(folder=folder)
    lfa.install()
    lfa.execute()
    print(lfa.buffer.data())
    
    
def test_010():
    
    folder = os.path.dirname(__file__)
    lfa = ListFilesAction(folder=folder, extension=".py")
    lfa.install()
    lfa.execute()
    print(lfa.buffer.data())