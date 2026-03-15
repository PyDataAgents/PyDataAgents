import os
import shutil
import pytesseract
from pdf2image import convert_from_path

from pydag.buffers.ListBuffer import ListBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.documents.OCRAction import OCRAction

def test_000():
    # make sure poopler is installed and on PATH (in windows)
    # https://github.com/oschwartz10612/poppler-windows/releases/tag/v25.11.0-0
    # make sure tesseract is installed and on PATH (in windows)
    # https://tesseract-ocr.github.io/tessdoc/Installation.html
    # https://github.com/UB-Mannheim/tesseract/wiki (for windows)
    
    # Convert PDF pages to PIL images
    pdf_path = os.path.dirname(__file__) + os.sep + "test.pdf"
    pages = convert_from_path(pdf_path)

    all_text = ""
    for page in pages:
        text = pytesseract.image_to_string(page)
        all_text += text + "\n"

    print(all_text)
    
def test_010():
    print("Tesseract:", shutil.which("tesseract"))
    print("pdfinfo:", shutil.which("pdfinfo"))
    print("pdftoppm:", shutil.which("pdftoppm"))
    
def test_020():
    
    fpath = os.path.dirname(__file__) + os.sep + "test.pdf"
    
    buf = ListBuffer()
    buf.install()
    
    buf.push(fpath)
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    oa = OCRAction()    
    oa.add_parent(lba)
    oa.install()
    
    print(buf.data(persistent=True))
    
    oa.execute()
    
    print(oa.get_buffer().data(persistent=True))
    
def test_030():
    fpath = os.path.dirname(__file__) + os.sep + "handwritten.jpg"
    
    buf = ListBuffer()
    buf.install()
    
    buf.push(fpath)
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    oa = OCRAction()    
    oa.add_parent(lba)
    oa.install()
    
    print(buf.data(persistent=True))
    
    oa.execute()
    
    print(oa.get_buffer().data(persistent=True))    
    t1 = oa.get_buffer().data(persistent=True)["text"][0]    
    assert t1 == '', "Expected no text to be extracted from handwritten image, but got: " + t1
    
def test_031():
    fpath = os.path.dirname(__file__) + os.sep + "scan_sample.pdf"
    
    buf = ListBuffer()
    buf.install()
    
    buf.push(fpath)
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    oa = OCRAction()    
    oa.add_parent(lba)
    oa.install()
    
    print(buf.data(persistent=True))
    
    oa.execute()
       
    print(oa.get_buffer().data(persistent=True))
    
    t1 = oa.get_buffer().data(persistent=True)["text"][0]    
    assert t1 is not ''

def test_032():
    fpath = os.path.dirname(__file__) + os.sep + "work_order1.png"
    
    buf = ListBuffer()
    buf.install()
    
    buf.push(fpath)
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    oa = OCRAction()    
    oa.add_parent(lba)
    oa.install()
    
    print(buf.data(persistent=True))
    
    oa.execute()
       
    print(oa.get_buffer().data(persistent=True))
    
    t1 = oa.get_buffer().data(persistent=True)["text"][0]    
    assert t1 is not ''
    
    
    