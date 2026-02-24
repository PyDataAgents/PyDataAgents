import os

from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.ConvertFile2Base64Action import ConvertFile2Base64Action


def test_000():
    
    file_paths = [os.path.dirname(__file__) + os.sep + "This is a Test PDF.pdf"]
    
    cf2b64a = ConvertFile2Base64Action(file_paths=file_paths)    
    cf2b64a.install()    
    cf2b64a.execute()    
    print(cf2b64a.get_buffer().data())
    
def test_010():
    file_paths = [os.path.dirname(__file__) + os.sep + "test-image.png"]
    
    cf2b64a = ConvertFile2Base64Action(file_paths=file_paths)
    
    cf2b64a.install()
    
    cf2b64a.execute()
    
    print(cf2b64a.get_buffer().data())
    

def test_020():
    file_paths = [os.path.dirname(__file__) + os.sep + "test-image.png"]
    
    buf = ListBuffer(capacity=2)
    buf.install()
    buf.push(file_paths)
    
    lba = LinkBufferAction()   
    lba.set_buffer(buf)
    lba.install() 
    
    cf2b64a = ConvertFile2Base64Action(input_keys=["values"])
    cf2b64a.install()
    cf2b64a.add_parent(lba)
    
    cf2b64a.execute()
    
    print(cf2b64a.get_buffer().data())
    
    
