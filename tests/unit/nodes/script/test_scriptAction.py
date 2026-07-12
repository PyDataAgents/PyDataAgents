import os

import pytest

from pydag.agents.AgentConfig import AgentConfig
from pydag.agents.AgentElementException import AgentElementException
from pydag.buffers.signals.SampledSine import SampledSine
from pydag.nodes.BufferNode import BufferNode
from pydag.nodes.NodeException import NodeException
from pydag.nodes.buffers.SampledSignalAction import SampledSignalAction
from pydag.nodes.script.ScriptAction import ScriptAction


TEST_SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "test scripts")
SCRIPT1_PATH = os.path.join(TEST_SCRIPTS_DIR, "script1.py")
SCRIPT2_PATH = os.path.join(TEST_SCRIPTS_DIR, "script2.py")
RUNTIME_ERROR_SCRIPT_PATH = os.path.join(TEST_SCRIPTS_DIR, "runtime_error.py")
REQUESTED_OUTPUT_ONLY_SCRIPT_PATH = os.path.join(TEST_SCRIPTS_DIR, "requested_output_only.py")
PARTIAL_OUTPUT_SCRIPT_PATH = os.path.join(TEST_SCRIPTS_DIR, "partial_output.py")
NO_OUTPUT_KEYS_SCRIPT_PATH = os.path.join(TEST_SCRIPTS_DIR, "no_output_keys.py")
MERGE_PARENT_DATA_SCRIPT_PATH = os.path.join(TEST_SCRIPTS_DIR, "merge_parent_data.py")


def _create_signal_parent() -> SampledSignalAction:
    signal = SampledSine(sample_rate=1000.0)
    parent = SampledSignalAction(signal=signal, n=2000)
    parent.install()
    return parent


def _create_buffer_parent(data: dict) -> BufferNode:
    parent = BufferNode()
    parent.install()
    parent.add_data(data)
    return parent


def _buffer_user_data(action: ScriptAction) -> dict:
    data = action.get_buffer().data()
    data.pop(AgentConfig.TIMESTAMPS, None)
    data.pop(AgentConfig.INDEX, None)
    return data


def test_install_requires_script_path():
    action = ScriptAction(output_keys=["result"], use_parent_data=False)

    with pytest.raises(AgentElementException):
        action.install()


def test_install_rejects_missing_script_file():
    missing_script_path = os.path.join(TEST_SCRIPTS_DIR, "missing_script.py")
    action = ScriptAction(script_path=missing_script_path, output_keys=["result"], use_parent_data=False)

    with pytest.raises(AgentElementException):
        action.install()


def test_execute_swallows_script_runtime_error_and_keeps_buffer_empty():
    action = ScriptAction(script_path=RUNTIME_ERROR_SCRIPT_PATH, output_keys=["result"], use_parent_data=False)
    action.install()

    action.execute()

    assert action.get_buffer().data() == {}


def test_execute_only_persists_requested_output_keys():
    action = ScriptAction(script_path=REQUESTED_OUTPUT_ONLY_SCRIPT_PATH, output_keys=["requested"], use_parent_data=False)
    action.install()

    action.execute()

    assert _buffer_user_data(action) == {"requested": [3.14]}


def test_execute_partial_output_only_writes_existing_keys():
    action = ScriptAction(script_path=PARTIAL_OUTPUT_SCRIPT_PATH, output_keys=["rms", "mean"], use_parent_data=False)
    action.install()

    action.execute()

    assert _buffer_user_data(action) == {"rms": [2.5]}


def test_execute_raises_when_ignore_empty_parents_is_false():
    parent = _create_signal_parent()
    parent.execute()

    action = ScriptAction(
        script_path=SCRIPT1_PATH,
        input_keys=["missing"],
        output_keys=["rms", "mean"],
        ignore_empty_parents=False,
    )
    action.add_parent(parent)
    action.install()

    with pytest.raises(NodeException, match="None of the specified input_keys were found in the parent buffers data"):
        action.execute()


def test_execute_with_no_output_keys_does_not_push_data():
    action = ScriptAction(script_path=NO_OUTPUT_KEYS_SCRIPT_PATH, use_parent_data=False)
    action.install()

    action.execute()

    assert action.get_buffer().data() == {}


def test_execute_with_multiple_parents_uses_merged_parent_data():
    parent_a = _create_buffer_parent({AgentConfig.VALUES: [1, 2]})
    parent_b = _create_buffer_parent({AgentConfig.VALUES: [3, 4]})
    action = ScriptAction(
        script_path=MERGE_PARENT_DATA_SCRIPT_PATH,
        input_keys=[AgentConfig.VALUES],
        output_keys=["merged_values"],
    )
    action.add_parent(parent_a)
    action.add_parent(parent_b)
    action.install()

    action.execute()

    assert _buffer_user_data(action) == {"merged_values": [1, 2, 3, 4]}


def test_execute_without_parent_data_writes_output():
    parent = _create_signal_parent()
    parent.execute()

    action = ScriptAction(
        script_path=SCRIPT2_PATH,
        use_parent_data=False,
        output_keys=["mode"],
    )
    action.add_parent(parent)
    action.install()

    action.execute()

    assert _buffer_user_data(action) == {"mode": ["standalone"]}


def test_execute_with_parent_data_enabled_keeps_current_behavior():
    parent = _create_signal_parent()
    parent.execute()

    action = ScriptAction(
        script_path=SCRIPT2_PATH,
        input_keys=[AgentConfig.VALUES],
        use_parent_data=True,
        output_keys=["mode"],
    )
    action.add_parent(parent)
    action.install()

    action.execute()

    assert _buffer_user_data(action) == {"mode": ["parent"]}
