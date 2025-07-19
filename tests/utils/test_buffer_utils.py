import os
from pydg.buffers.DictBuffer import DictBuffer
from pydg.utils.BufferUtils import BufferUtils


def test_000():
    buf = DictBuffer()
    buf.capacity = 3
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    buf.push({"C1": 5, "C2": 6})
    html = BufferUtils.dict_buffer_to_html(buf)
    print(html)
    
def test010():
    buf = DictBuffer()
    buf.capacity = 3
    buf.push({"C1": 1, "C2": 2})
    buf.push({"C1": 3, "C2": 4})
    buf.push({"C1": 5, "C2": 6})
    html = BufferUtils.dict_buffer_to_html(buf)
    path = os.getcwd() + "\\tests\\data\\table_html.html"
    with open(path, "w") as f:
        f.write(html)
    