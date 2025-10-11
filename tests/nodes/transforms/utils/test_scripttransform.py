import os


from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.TransformElement import TransformElement
from pydag.nodes.transforms.utils.ScriptTransform import ScriptTransform


def test_000():
    
    context_vars = ["dt", "t", "t_new", "n_m", "n_new"]
    output_vars = ["n_m", "dt"]
    script_file = os.path.dirname(__file__) + os.sep + "script1.py"
    
    buf = DictBuffer(capacity=10)
    buf.install()
    buf.push({"t_new": 1.0, "n_new": 100.0})
    buf.push({"t_new": 2.0, "n_new": 66.0})
    buf.push({"t_new": 3.0, "n_new": 80.0})
    buf.push({"t_new": 4.0, "n_new": 100.0})
    buf.push({"t_new": 5.0, "n_new": 45.0})
    
    lba = LinkBufferAction()
    lba.install()
    lba.buffer = buf
    
    buf2 = DictBuffer(capacity=1)   
    st = ScriptTransform(script_file=script_file, context_variables=context_vars, output_variables=output_vars)    
    te = TransformElement(transforms=[st], n=1, persistent=False)
    te.buffer = buf2
    te.install()
    te.add_parent(lba)
    
    for i in range(5):
        te.execute()
        print(te.buffer.data())