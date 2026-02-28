import os
import pytest
from pydag.buffers.signals.SampledSine import SampledSine
from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode
from pydag.nodes.buffers.SampledSignalAction import SampledSignalAction
from pydag.nodes.script.ScriptAction import ScriptAction
from pydag.nodes.NodeException import NodeException
from pydag.agents.AgentConfig import AgentConfig


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
            print(n.get_buffer().data())
            
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
            print(n.get_buffer().data())


def test_020_empty_parent_buffers():
    # Parent exists but has no data; ScriptAction should return without pushing output
    s = SampledSine(sample_rate=1000.0)
    ssa = SampledSignalAction(signal=s, n=2000)
    ssa.install()

    script_path = os.path.dirname(__file__) + os.sep + "script1.py"
    sa = ScriptAction(script_path=script_path, input_keys=["values"], output_keys=["rms", "mean"])
    sa.add_parent(ssa)
    sa.install()

    # Do NOT execute parent; buffer stays empty
    sa.execute()

    # No output should be produced when parent buffers are empty
    assert sa.get_buffer().data() == {}, "Expected empty dict output when parent buffers are empty, but got: " + str(sa.get_buffer().data())


@pytest.mark.skip(reason="This test is flaky and needs to be fixed. which behavior do we want in buffernode for non existent keys")
def test_030_non_matching_input_keys_raises():
    # Parent has data but input_keys do not match; ScriptAction should raise
    s = SampledSine(sample_rate=1000.0)
    ssa = SampledSignalAction(signal=s, n=2000)
    ssa.install()
    ssa.execute()  # populate parent buffer with 'values'

    script_path = os.path.dirname(__file__) + os.sep + "script1.py"
    sa = ScriptAction(script_path=script_path, input_keys=["nonexistent_key"], output_keys=["rms", "mean"])
    sa.add_parent(ssa)
    sa.install()

    with pytest.raises(NodeException):
        sa.execute()

def test_050_empty_dict_parent_data():
    # Use SampledSignalAction parent but override its buffer to return an empty dict
    s = SampledSine(sample_rate=1000.0)
    ssa = SampledSignalAction(signal=s, n=2000)
    ssa.install()

    buf = ssa.get_buffer()

    def empty_dict(n=0, persistent=True):
        return {}

    buf.data = empty_dict

    script_path = os.path.dirname(__file__) + os.sep + "script1.py"
    sa = ScriptAction(script_path=script_path, input_keys=[AgentConfig.VALUES], output_keys=["rms", "mean"])
    sa.add_parent(ssa)
    sa.install()

    # Execute; empty dict should be treated as empty data
    sa.execute()
    assert sa.get_buffer().data() == {}, "Expected empty dict output when parent buffer returns empty dict, but got: " + str(sa.get_buffer().data())
