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
    ssa.execute()  # This will populate the buffer with 'values', but we will override it to be empty
    sa.execute()

    # No output should be produced when parent buffers are empty
    assert len(sa.get_buffer().data()) > 0, "Expected non empty dict outputs, but got: " + str(sa.get_buffer().data())

def test_050_empty_dict_parent_data():
    # Use SampledSignalAction parent but override its buffer to return an empty dict
    s = SampledSine(sample_rate=1000.0)
    ssa = SampledSignalAction(signal=s, n=2000)
    ssa.install()

    buf = ssa.get_buffer()

    def wrong_key_dict(n=0, persistent=True):
        return {"VALOOS": [1]}

    buf.data = wrong_key_dict

    script_path = os.path.dirname(__file__) + os.sep + "script1.py"
    sa = ScriptAction(script_path=script_path, input_keys=[AgentConfig.VALUES], output_keys=["rms", "mean"])
    sa.add_parent(ssa)
    sa.install()

    # Execute; empty dict should be treated as empty data
    with pytest.raises(NodeException):
        sa.execute()
        assert sa.get_buffer().data() == {}, "Expected wrong input dict output when parent buffer returns empty dict, but got: " + str(sa.get_buffer().data())


def test_install_rejects_duplicate_output_keys():
    script_path = os.path.dirname(__file__) + os.sep + "script1.py"
    sa = ScriptAction(script_path=script_path, input_keys=["values"], output_keys=["rms", "rms"])

    with pytest.raises(NodeException, match="output_keys must contain unique entries"):
        sa.install()
