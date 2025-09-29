import os
from pydag.buffers.signals.SampledSine import SampledSine
from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode
from pydag.nodes.buffers.SampledSignalAction import SampledSignalAction
from pydag.nodes.script.ScriptAction import ScriptAction


def test_000():
    
    s = SampledSine(sample_rate=1000.0)
    ssa = SampledSignalAction(signal=s, n=2000)
    ssa.install()
    
    script_path = os.path.dirname(__file__) + os.sep + "script1.py"
    sa = ScriptAction(script_path=script_path, input_keys=["values"], output_keys=["rms", "mean"])
    sa.add_parent(ssa)
    sa.install()
        
    nodes : list[Action] = [ssa, sa]
    
    for n in nodes:
        n.execute()
        if isinstance(n, BufferNode):
            print(n.buffer.data())
            
def test_010():    
    s = SampledSine(sample_rate=1000.0)
    ssa = SampledSignalAction(signal=s, n=2000)
    ssa.install()
    
    script_path = os.path.dirname(__file__) + os.sep + "script1.py"
    sa = ScriptAction(script_path=script_path, input_keys=["values"], output_keys=["rms", "mean"])
    sa.add_parent(ssa)
    sa.install()
        
    nodes : list[Action] = [ssa, sa]
    
    for n in nodes:
        n.execute()
        if isinstance(n, BufferNode):
            print(n.buffer.data())
        