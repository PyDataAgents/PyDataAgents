from pydg.buffers.DictBuffer import DictBuffer
from pydg.statemachine.actions.buffers.FormattedStringAction import FormattedStringAction
from pydg.statemachine.actions.buffers.LinkBufferAction import LinkBufferAction


def test_000():
    
    s = "Hi {}, are you from {}"
    i = ["Joe", "Mexico"]
    
    msg = s.format(*i)
    
    print(msg)
    
def test_010():
    
    buf = DictBuffer()
    buf.capacity = 2
    buf.push({"name": "Joe", "town": "Berlin"})
    buf.push({"name": "John", "town": "Amsterdam"})
    
    lba = LinkBufferAction()
    lba.buffer = buf
    
    fsa = FormattedStringAction()
    fsa.data_keys = ["name", "town"]
    fsa.template = "Hi {}, are you from {}"
    fsa.add_parent(lba)
    
    fsa.install()
    
    fsa.execute()
    
    print(fsa.buffer.data())
    