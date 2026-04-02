import os

from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.NodeException import NodeException
from pydag.nodes.documents.ReadXMLAction import ReadXMLAction


def test_action_with_dictbuffer():
    file_path = os.path.dirname(__file__) + os.sep + "book.xml"
    xpath = "//book/title/text()"
    
    rxa = ReadXMLAction(file_path = file_path, xpath = xpath)
    
    rxa.install()
    rxa.execute()    
    
    d = rxa.get_buffer().data()
    print(d)    
    
    assert "values" in d, "values tag was not found in buffer data"
    assert len(d["values"]) == 2, "the wrong amount of list entries were returned"
    
    

def test_action_with_ouput_keys():
    file_path = os.path.dirname(__file__) + os.sep + "book.xml"
    xpath = "//book/title/text()"
    
    rxa = ReadXMLAction(file_path = file_path, xpath = xpath, output_keys=["xml"])
    
    rxa.install()
    rxa.execute()
    
    d = rxa.get_buffer().data()
    print(d)
    
    assert "xml" in d, "xml tag was not found in buffer data"
    assert len(d["xml"]) == 2, "the wrong amount of list entries were returned"
    
def test_with_too_many_output_keys():
    file_path = os.path.dirname(__file__) + os.sep + "book.xml"
    xpath = "//book/title/text()"
    
    rxa = ReadXMLAction(file_path = file_path, xpath = xpath, output_keys=["xml", "xml2"])
    
    rxa.install()
    
    
    try:
        rxa.execute()
        d = rxa.get_buffer().data()
        print(d)
        assert False, "should have thrown a NodeException"
    except NodeException:
        assert True
        
def test_with_listbuffer():
    file_path = os.path.dirname(__file__) + os.sep + "book.xml"
    xpath = "//book/title/text()"
    
    buf = ListBuffer()
    buf.install()
    
    rxa = ReadXMLAction(file_path = file_path, xpath = xpath)
    rxa.set_buffer(buf)
    rxa.install()
    rxa.execute()    
    
    d = rxa.get_buffer().data()
    print(d)    
    
    assert "values" in d, "values tag was not found in buffer data"
    assert len(d["values"]) == 2, "the wrong amount of list entries were returned"
    
def test_with_element_return():
    file_path = os.path.dirname(__file__) + os.sep + "book.xml"
    xpath = "//book/title"
    
    buf = ListBuffer()
    buf.install()
    
    rxa = ReadXMLAction(file_path = file_path, xpath = xpath)
    rxa.set_buffer(buf)
    rxa.install()
    rxa.execute()    
    
    d = rxa.get_buffer().data()
    print(d)    
    
    assert "values" in d, "values tag was not found in buffer data"
    assert len(d["values"]) == 2, "the wrong amount of list entries were returned"
    
def test_with_element_return2():
    file_path = os.path.dirname(__file__) + os.sep + "book.xml"
    xpath = "//book/title"
    
    buf = DictBuffer()
    buf.install()
    
    rxa = ReadXMLAction(file_path = file_path, xpath = xpath)
    rxa.set_buffer(buf)
    rxa.install()
    rxa.execute()    
    
    d = rxa.get_buffer().data()
    print(d)    
    
    assert "title" in d, "values tag was not found in buffer data"
    assert len(d["title"]) == 2, "the wrong amount of list entries were returned"
    
def test_attributes():
    file_path = os.path.dirname(__file__) + os.sep + "book.xml"
    xpath = "//book/@id"
        
    rxa = ReadXMLAction(file_path = file_path, xpath = xpath)
    rxa.install()
    rxa.execute() 
    
    d = rxa.get_buffer().data()
    print(d)
    
    assert "values" in d, "values tag was not found in buffer data"
    assert len(d["values"]) == 2, "the wrong amount of list entries were returned"
    