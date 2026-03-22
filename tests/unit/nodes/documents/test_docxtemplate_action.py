import os
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.documents.DocxTemplateAction import DocxTemplateAction


def test_000():
    
    dic1 = {
        "heading1": "Template Example",
        "user": "John Doe",
        "age": 34,
        "other_user": "Bob Dylan",
        "items": ["GER", "USA", "UK", "FR"]
    }    
    buf1 = DictBuffer(initial_values=dic1)
    buf1.install()
    
    template_path = os.path.dirname(__file__) + os.sep + "template1.docx"
    output_path = os.path.dirname(__file__) + os.sep + "test_out1.docx"
    
    docx_action = DocxTemplateAction(template_path=template_path, output_path=output_path)
    docx_action.set_buffer(buf1)
    
    docx_action.install()
    
    docx_action.execute()
        
