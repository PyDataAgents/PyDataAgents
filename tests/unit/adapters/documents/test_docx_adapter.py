import os
from pydag.adapters.documents.DocxAdapter import DocxAdapter
from pydag.buffers.DictBuffer import DictBuffer


def test_000():
    
    template_path = os.path.dirname(__file__) + os.sep + "template1.docx"
    output_path = os.path.dirname(__file__) + os.sep + "test_out1.docx"
    
    da = DocxAdapter(template_path=template_path, output_path=output_path)
    
    dic1 = {
        "heading1": "Template Example",
        "user": "John Doe",
        "age": 34,
        "other_user": "Bob Dylan"
    }    
    buf1 = DictBuffer(initial_values=dic1)
    buf1.install()
    
    dic2 = {
        "items" : ["Germany", "UK", "USA", "Uganda"]
    }
    buf2 = DictBuffer(initial_values=dic2)
    buf2.install()
    
    buffers = buf1.to_dict()
    buffers.update(buf2.to_dict())
    
    da.install()
    da.connect()
    
    da.write_to_sink(buffers=buffers, addresses=[], n = 0, persistent = True)
    
    da.disconnect()
    
    da.uninstall()
    