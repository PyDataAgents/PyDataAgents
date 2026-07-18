import os
from pydag.services.MappingType import MappingType
from pydag.services.ThreadType import ThreadType
from pydag.services.documents.DocxService import DocxService
from pydag.buffers.DictBuffer import DictBuffer


def test_000():
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
    
    template_path = os.path.dirname(__file__) + os.sep + "template1.docx"
    output_path = os.path.dirname(__file__) + os.sep + "test_out1.docx"
    
    da = DocxService(n=0,template_path=template_path, output_path=output_path, thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.WRITE.value)
    da.add_buffer(buf1)
    da.add_buffer(buf2)
    
    da.install()
    
    da.write_to_sink()
        
    da.uninstall()
    
