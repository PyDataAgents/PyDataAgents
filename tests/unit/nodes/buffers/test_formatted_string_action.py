import pytest

from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.NodeException import NodeException
from pydag.nodes.buffers.FormattedStringAction import FormattedStringAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction


def test_000():
    
    s = "Hi {}, are you from {}"
    i = ["Joe", "Mexico"]
    
    msg = s.format(*i)
    
    print(msg)
    
def test_010():
    
    buf = DictBuffer(capacity = 2)
    buf.install()
    buf.push({"name": "Joe", "town": "Berlin"})
    buf.push({"name": "John", "town": "Amsterdam"})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    lba.install()
    
    fsa = FormattedStringAction()
    fsa.input_keys = ["name", "town"]
    fsa.template = "Hi {}, are you from {}"
    fsa.add_parent(lba)
    
    fsa.install()
    
    fsa.execute()
    
    print(fsa.get_buffer().data())
    
def test_020():
    
    buf = DictBuffer(capacity = 2)
    buf.install()
    buf.push({"name": "Joe", "town": "Berlin"})
    buf.push({"name": "John", "town": "Amsterdam"})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    
    fsa = FormattedStringAction()
    fsa.input_keys = ["town", "name"]
    fsa.template = "Hi {1}, are you from {0}"
    fsa.add_parent(lba)
    
    fsa.install()
    
    fsa.execute()
    
    print(fsa.get_buffer().data())
    
def test_021():
    
    buf = DictBuffer(capacity = 2)
    buf.install()
    buf.push({"name": "Joe", "town": "Berlin"})
    buf.push({"name": "John", "town": "Amsterdam"})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    
    fsa = FormattedStringAction()
    fsa.input_keys = ["name", "town"]
    fsa.template = "Hi {1}, are you from {0}"
    fsa.add_parent(lba)
    
    fsa.install()
    
    fsa.execute()
    
    print(fsa.get_buffer().data())
    
    
def test_022():
    
    buf = DictBuffer(capacity = 2)
    buf.install()
    buf.push({"name": "Joe", "town": "Berlin"})
    buf.push({"name": "John", "town": "Amsterdam"})
    
    lba = LinkBufferAction()
    lba.set_buffer(buf)
    
    fsa = FormattedStringAction(output_keys=["question"])
    fsa.input_keys = ["name", "town"]
    fsa.template = "Hi {0}, are you from {1}"
    fsa.add_parent(lba)
    
    fsa.install()
    
    fsa.execute()
    
    print(fsa.get_buffer().data())


def test_install_rejects_duplicate_input_keys():
    fsa = FormattedStringAction()
    fsa.input_keys = ["name", "name"]
    fsa.template = "Hi {}, are you from {}"

    with pytest.raises(NodeException, match="input_keys must contain unique entries"):
        fsa.install()
    
