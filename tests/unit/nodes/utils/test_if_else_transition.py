import pytest

from pydag.agents.AgentElementException import AgentElementException
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.NodeException import NodeException
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.buffers.CopyDataAction import CopyDataAction
from pydag.nodes.utils.IfElseTransition import IfElseTransition
from pydag.nodes.utils.TrueTransition import TrueTransition
from pydag.nodes.utils.StopAction import StopAction
from pydag.services.ThreadType import ThreadType
from pydag.services.statemachine.SFCService import SFCService


def make_transition(data=None, **kwargs):
    parent = LinkBufferAction()
    buffer = DictBuffer(index_enabled=False, timestamps_enabled=False)
    buffer.install()
    if data:
        buffer.push(data)
    parent.set_buffer(buffer)
    parent.install()
    node = IfElseTransition(**kwargs)
    parent.add_child(node)
    node.add_child(CopyDataAction(id="yes"))
    node.add_child(CopyDataAction(id="no"))
    node.install()
    return parent, node


@pytest.mark.parametrize("condition,value,expected", [
    ("equals", 90, "yes"), ("not_equals", 90, "no"),
    ("greater_than", 80, "yes"), ("greater_or_equal", 90, "yes"),
    ("less_than", 80, "no"), ("less_or_equal", 90, "yes"),
    ("exists", None, "yes"), ("is_null", None, "no"),
    ("is_not_null", None, "yes"),
])
def test_conditions(condition, value, expected):
    parent, node = make_transition({"temperature": [20, 90]},
                                   json_path="$.temperature[-1]", condition=condition, value=value)
    assert node.get_next_children() == []
    assert node.check() is True
    assert node.get_next_children()[0].id == expected
    assert parent.get_buffer().data(persistent=True)["temperature"] == [20, 90]
    assert node.get_buffer().data(persistent=True)["temperature"] == [20, 90]
    assert len(node.get_children()) == 2


@pytest.mark.parametrize("mode,expected", [("any", "yes"), ("all", "no")])
def test_wildcard_match_modes(mode, expected):
    _, node = make_transition({"temperature": [20, 90]}, json_path="$.temperature[*]",
                              condition="greater_than", value=80, match_mode=mode)
    node.check()
    assert node.get_next_children()[0].id == expected


@pytest.mark.parametrize("mode", ["any", "all"])
def test_missing_path_is_false_even_for_all(mode):
    _, node = make_transition({"value": [1]}, json_path="$.missing", condition="exists", match_mode=mode)
    node.check()
    assert node.get_next_children()[0].id == "no"


def test_nested_json_and_contains():
    _, node = make_transition({"payload": [{"message": "motor overheated"}]},
                              json_path="$.payload[0].message", condition="contains", value="overheated")
    node.check()
    assert node.get_next_children()[0].id == "yes"


def test_empty_parent_selects_else():
    _, node = make_transition(json_path="$.temperature[*]", condition="exists")
    node.check()
    assert node.get_next_children()[0].id == "no"


def test_repeated_checks_replace_payload_and_branch():
    parent, node = make_transition({"value": [1]}, json_path="$.value[0]", value=1, persistent=False)
    node.check()
    assert node.get_next_children()[0].id == "yes"
    assert parent.get_buffer().size() == 0
    parent.add_data({"value": [2]})
    node.check()
    assert node.get_next_children()[0].id == "no"
    assert node.get_buffer().data(persistent=True)["value"] == [2]


@pytest.mark.parametrize("kwargs", [
    {"json_path": "$["}, {"json_path": ""}, {"condition": "unknown"},
    {"match_mode": "unknown"}, {"n": -1},
])
def test_invalid_configuration(kwargs):
    with pytest.raises(AgentElementException):
        make_transition(**kwargs)


@pytest.mark.parametrize("count", [0, 1, 3])
def test_requires_two_children(count):
    node = IfElseTransition()
    for _ in range(count):
        node.add_child(TrueTransition())
    with pytest.raises(AgentElementException, match="two distinct children"):
        node.install()


def test_invalid_data_does_not_select_a_branch():
    _, node = make_transition({"value": ["text"]}, json_path="$.value[0]", condition="greater_than", value=1)
    with pytest.raises(NodeException, match="Cannot evaluate"):
        node.check()
    assert node.get_next_children() == []


@pytest.mark.parametrize("value,selected", [(1, "yes"), (2, "no")])
@pytest.mark.parametrize("configured", [False, True])
def test_sfc_executes_only_selected_child(value, selected, configured):
    parent, node = make_transition({"value": [value]}, json_path="$.value[0]", value=1)
    yes, no = node.get_children()
    yes_stop, no_stop = StopAction(), StopAction()
    yes.add_child(yes_stop)
    no.add_child(no_stop)
    nodes = [parent, node, yes, no, yes_stop, no_stop]
    if configured:
        # Reconstruct configuration without runtime edges, in parent-first order.
        nodes = [type(item)(**item.config_options()) for item in nodes]
        parent, node, yes, no, yes_stop, no_stop = nodes
        parent.install()
        parent.add_data({"value": [value]})
    service = SFCService(thread_type=ThreadType.ONLY_ONCE.value)
    for item in nodes:
        service.add_node(item)
    service.install()
    service.start()
    service._thread.join(timeout=2)
    assert not service._thread.is_alive()
    chosen, other = (yes, no) if selected == "yes" else (no, yes)
    assert chosen.get_buffer().data(persistent=True)["value"] == [value]
    assert other.get_buffer().size() == 0
    assert chosen.get_last_timestamp() > 0
    assert other.get_last_timestamp() == 0


def test_normal_transition_keeps_all_children():
    node = TrueTransition()
    node.add_child(StopAction())
    node.add_child(StopAction())
    assert node.get_next_children() == node.get_children()
