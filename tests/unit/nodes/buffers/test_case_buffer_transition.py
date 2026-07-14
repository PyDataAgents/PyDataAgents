import pytest

from pydag.agents.AgentElementException import AgentElementException
from pydag.buffers.Comparator import Comparator
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.NodeException import NodeException
from pydag.nodes.buffers.CaseBufferTransition import CaseBufferTransition
from pydag.nodes.buffers.CopyDataAction import CopyDataAction
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction


def _parent_with_data(data: dict) -> LinkBufferAction:
    buffer = DictBuffer(index_enabled=False, timestamps_enabled=False)
    buffer.install()
    buffer.push(data)

    parent = LinkBufferAction()
    parent.set_buffer(buffer)
    parent.install()
    return parent


def _empty_parent() -> LinkBufferAction:
    buffer = DictBuffer(index_enabled=False, timestamps_enabled=False)
    buffer.install()

    parent = LinkBufferAction()
    parent.set_buffer(buffer)
    parent.install()
    return parent


def _case_transition(parent: LinkBufferAction, **kwargs) -> CaseBufferTransition:
    transition = CaseBufferTransition(**kwargs)
    buffer = DictBuffer(index_enabled=False, timestamps_enabled=False)
    buffer.install()
    transition.set_buffer(buffer)
    transition.add_parent(parent)
    transition.install()
    return transition


def _child_reader(parent: CaseBufferTransition, persistent: bool = True) -> CopyDataAction:
    child = CopyDataAction(persistent=persistent)
    buffer = DictBuffer(index_enabled=False, timestamps_enabled=False)
    buffer.install()
    child.set_buffer(buffer)
    child.add_parent(parent)
    child.install()
    return child


def _matching_transition_with_payload() -> CaseBufferTransition:
    parent = _parent_with_data(
        {
            "case": ["route", "route"],
            "value": [1, 2],
        }
    )
    transition = _case_transition(
        parent,
        case_key="case",
        comparator=Comparator.EQUAL.value,
        value="route",
        check_n=1,
        payload_n=2,
    )

    assert transition.check() is True
    return transition


def test_true_case_moves_payload_from_parent_to_transition_buffer():
    parent = _parent_with_data(
        {
            "case": ["5", "5", "other", "other"],
            "value": [1, 2, 3, 4],
        }
    )
    transition = _case_transition(
        parent,
        case_key="case",
        comparator=Comparator.EQUAL.value,
        value="5",
        check_n=1,
        payload_n=2,
    )

    assert transition.check() is True

    assert parent.get_buffer().size() == 2
    assert parent.get_buffer().data(persistent=True)["value"] == [3, 4]
    assert transition.get_buffer().size() == 2
    assert transition.get_buffer().data(persistent=True) == {
        "case": ["5", "5"],
        "value": [1, 2],
    }


def test_false_case_does_not_move_payload_from_parent():
    parent = _parent_with_data(
        {
            "case": ["3", "3", "3"],
            "value": [1, 2, 3],
        }
    )
    transition = _case_transition(
        parent,
        case_key="case",
        comparator=Comparator.EQUAL.value,
        value="5",
        check_n=1,
        payload_n=2,
    )

    assert transition.check() is False

    assert parent.get_buffer().size() == 3
    assert parent.get_buffer().data(persistent=True)["value"] == [1, 2, 3]
    assert transition.get_buffer().size() == 0


def test_payload_is_collected_only_after_condition_check_passes():
    parent = _parent_with_data(
        {
            "case": ["reject", "accept"],
            "value": [1, 2],
        }
    )
    transition = _case_transition(
        parent,
        case_key="case",
        comparator=Comparator.EQUAL.value,
        value="accept",
        check_n=1,
        payload_n=1,
    )

    assert transition.check() is False

    assert parent.get_buffer().size() == 2
    assert parent.get_buffer().data(persistent=True)["case"] == ["reject", "accept"]
    assert transition.get_buffer().size() == 0


def test_payload_keys_select_forwarded_columns_while_moving_rows_from_parent():
    parent = _parent_with_data(
        {
            "case": ["route", "route"],
            "value": [10, 20],
            "unused": ["a", "b"],
        }
    )
    transition = _case_transition(
        parent,
        case_key="case",
        comparator=Comparator.EQUAL.value,
        value="route",
        check_n=1,
        payload_n=1,
        payload_keys=["value"],
    )

    assert transition.check() is True

    assert parent.get_buffer().size() == 1
    assert transition.get_buffer().data(persistent=True) == {"value": [10]}


def test_missing_payload_keys_raise_without_moving_parent_data():
    parent = _parent_with_data(
        {
            "case": ["route", "route"],
            "value": [10, 20],
        }
    )
    transition = _case_transition(
        parent,
        case_key="case",
        comparator=Comparator.EQUAL.value,
        value="route",
        check_n=1,
        payload_n=1,
        payload_keys=["missing"],
    )

    with pytest.raises(NodeException, match="None of the specified input_keys"):
        transition.check()

    assert parent.get_buffer().size() == 2
    assert parent.get_buffer().data(persistent=True)["value"] == [10, 20]
    assert transition.get_buffer().size() == 0


def test_missing_case_key_raises_without_moving_parent_data():
    parent = _parent_with_data(
        {
            "value": [10, 20],
        }
    )
    transition = _case_transition(
        parent,
        case_key="case",
        comparator=Comparator.EQUAL.value,
        value="route",
        check_n=1,
        payload_n=1,
    )

    with pytest.raises(NodeException, match="case_key 'case' was not found"):
        transition.check()

    assert parent.get_buffer().size() == 2
    assert parent.get_buffer().data(persistent=True)["value"] == [10, 20]
    assert transition.get_buffer().size() == 0


def test_default_case_moves_payload_without_case_key():
    parent = _parent_with_data(
        {
            "value": [1, 2, 3],
        }
    )
    transition = _case_transition(parent, default=True, payload_n=2)

    assert transition.check() is True

    assert parent.get_buffer().size() == 1
    assert transition.get_buffer().data(persistent=True) == {"value": [1, 2]}


def test_one_to_many_children_all_persistent_read_same_transition_payload():
    transition = _matching_transition_with_payload()
    expected_payload = {"case": ["route", "route"], "value": [1, 2]}
    children = [
        _child_reader(transition, persistent=True),
        _child_reader(transition, persistent=True),
        _child_reader(transition, persistent=True),
    ]

    for child in children:
        child.execute()

    assert transition.get_children() == children
    assert [child.get_buffer().data(persistent=True) for child in children] == [
        expected_payload,
        expected_payload,
        expected_payload,
    ]
    assert transition.get_buffer().data(persistent=True) == expected_payload


def test_one_to_many_children_first_non_persistent_reader_consumes_transition_payload():
    transition = _matching_transition_with_payload()
    expected_payload = {"case": ["route", "route"], "value": [1, 2]}
    children = [
        _child_reader(transition, persistent=False),
        _child_reader(transition, persistent=True),
        _child_reader(transition, persistent=True),
    ]

    for child in children:
        child.execute()

    assert transition.get_children() == children
    assert [child.get_buffer().data(persistent=True) for child in children] == [
        expected_payload,
        {},
        {},
    ]
    assert transition.get_buffer().size() == 0


def test_one_to_many_children_last_non_persistent_reader_consumes_transition_payload_after_others_read():
    transition = _matching_transition_with_payload()
    expected_payload = {"case": ["route", "route"], "value": [1, 2]}
    children = [
        _child_reader(transition, persistent=True),
        _child_reader(transition, persistent=True),
        _child_reader(transition, persistent=False),
    ]

    for child in children:
        child.execute()

    assert transition.get_children() == children
    assert [child.get_buffer().data(persistent=True) for child in children] == [
        expected_payload,
        expected_payload,
        expected_payload,
    ]
    assert transition.get_buffer().size() == 0


def test_one_to_many_children_middle_non_persistent_reader_consumes_transition_payload_for_later_child():
    transition = _matching_transition_with_payload()
    expected_payload = {"case": ["route", "route"], "value": [1, 2]}
    children = [
        _child_reader(transition, persistent=True),
        _child_reader(transition, persistent=False),
        _child_reader(transition, persistent=True),
    ]

    for child in children:
        child.execute()

    assert transition.get_children() == children
    assert [child.get_buffer().data(persistent=True) for child in children] == [
        expected_payload,
        expected_payload,
        {},
    ]
    assert transition.get_buffer().size() == 0


def test_empty_parent_buffer_returns_false_without_error():
    parent = _empty_parent()
    transition = _case_transition(
        parent,
        case_key="case",
        comparator=Comparator.EQUAL.value,
        value="route",
        check_n=1,
        payload_n=1,
    )

    assert transition.check() is False
    assert parent.get_buffer().size() == 0
    assert transition.get_buffer().size() == 0


def test_empty_parent_buffer_returns_false_for_default_branch():
    parent = _empty_parent()
    transition = _case_transition(parent, default=True, payload_n=1)

    assert transition.check() is False
    assert parent.get_buffer().size() == 0
    assert transition.get_buffer().size() == 0


def test_case_check_returns_false_if_parent_data_disappears_during_check(monkeypatch):
    parent = _parent_with_data({"case": ["route"], "value": [1]})
    transition = _case_transition(
        parent,
        case_key="case",
        comparator=Comparator.EQUAL.value,
        value="route",
        check_n=1,
        payload_n=1,
    )
    has_data_results = iter([True, False])

    monkeypatch.setattr(transition, "_parent_buffers_have_data", lambda: next(has_data_results))
    monkeypatch.setattr(transition, "_read_parent_data", lambda **kwargs: {})

    assert transition.check() is False
    assert transition.get_buffer().size() == 0


def test_case_check_returns_false_if_case_key_exists_but_no_case_data_is_available(monkeypatch):
    parent = _parent_with_data({"case": ["route"], "value": [1]})
    transition = _case_transition(
        parent,
        case_key="case",
        comparator=Comparator.EQUAL.value,
        value="route",
        check_n=1,
        payload_n=1,
    )

    monkeypatch.setattr(transition, "_read_parent_data", lambda **kwargs: {})
    monkeypatch.setattr(transition, "_parent_buffers_contain_key", lambda key: True)

    assert transition.check() is False
    assert transition.get_buffer().size() == 0


@pytest.mark.parametrize(
    ("comparator", "actual", "expected", "passes"),
    [
        (Comparator.EQUAL.value, "topic_1", "topic_1", True),
        (Comparator.NOT_EQUAL.value, "topic_1", "topic_2", True),
        (Comparator.GREATER.value, 7, 5, True),
        (Comparator.LESS.value, 3, 5, True),
        (Comparator.EQUAL_OR_GREATER.value, 5, 5, True),
        (Comparator.EQUAL_OR_LESS.value, 5, 5, True),
        (Comparator.LIKE.value, "support request", "support", True),
        (Comparator.NOT_LIKE.value, "sales request", "support", True),
        (Comparator.NOT_NULL.value, "not empty", None, True),
        (CaseBufferTransition.REGEX, "topic_42", r"topic_\d+", True),
        (Comparator.EQUAL.value, "topic_1", "topic_2", False),
    ],
)
def test_supported_comparators(comparator, actual, expected, passes):
    parent = _parent_with_data(
        {
            "case": [actual],
            "value": [1],
        }
    )
    transition = _case_transition(
        parent,
        case_key="case",
        comparator=comparator,
        value=expected,
        check_n=1,
        payload_n=1,
    )

    assert transition.check() is passes

    if passes:
        assert parent.get_buffer().size() == 0
        assert transition.get_buffer().size() == 1
    else:
        assert parent.get_buffer().size() == 1
        assert transition.get_buffer().size() == 0


@pytest.mark.parametrize(
    ("comparator", "actual", "expected"),
    [
        ("==", "topic_1", "topic_1"),
        ("!=", "topic_1", "topic_2"),
        (">", 7, 5),
        ("<", 3, 5),
        (">=", 5, 5),
        ("<=", 5, 5),
    ],
)
def test_python_style_symbolic_comparators(comparator, actual, expected):
    parent = _parent_with_data(
        {
            "case": [actual],
            "value": [1],
        }
    )
    transition = _case_transition(
        parent,
        case_key="case",
        comparator=comparator,
        value=expected,
        check_n=1,
        payload_n=1,
    )

    assert transition.check() is True
    assert parent.get_buffer().size() == 0
    assert transition.get_buffer().size() == 1


def test_check_n_can_match_any_checked_value():
    parent = _parent_with_data(
        {
            "case": ["skip", "route", "later"],
            "value": [1, 2, 3],
        }
    )
    transition = _case_transition(
        parent,
        case_key="case",
        comparator=Comparator.EQUAL.value,
        value="route",
        check_n=2,
        payload_n=2,
    )

    assert transition.check() is True
    assert transition.get_buffer().data(persistent=True)["value"] == [1, 2]
    assert parent.get_buffer().data(persistent=True)["value"] == [3]


def test_payload_key_validation_rejects_duplicate_keys_on_install():
    parent = _parent_with_data({"case": ["route"], "value": [1]})
    transition = CaseBufferTransition(
        case_key="case",
        comparator=Comparator.EQUAL.value,
        value="route",
        payload_keys=["value", "value"],
    )
    transition.add_parent(parent)

    with pytest.raises(AgentElementException):
        transition.install()


def test_install_rejects_missing_case_key_for_non_default_transition():
    parent = _parent_with_data({"case": ["route"], "value": [1]})
    transition = CaseBufferTransition()
    transition.add_parent(parent)

    with pytest.raises(AgentElementException):
        transition.install()


def test_install_rejects_unsupported_comparator():
    parent = _parent_with_data({"case": ["route"], "value": [1]})
    transition = CaseBufferTransition(case_key="case", comparator="UNKNOWN")
    transition.add_parent(parent)

    with pytest.raises(AgentElementException):
        transition.install()


def test_install_rejects_negative_check_or_payload_n():
    parent = _parent_with_data({"case": ["route"], "value": [1]})

    transition = CaseBufferTransition(case_key="case", check_n=-1)
    transition.add_parent(parent)
    with pytest.raises(AgentElementException):
        transition.install()

    transition = CaseBufferTransition(case_key="case", payload_n=-1)
    transition.add_parent(parent)
    with pytest.raises(AgentElementException):
        transition.install()


def test_check_without_parent_raises_node_exception():
    transition = CaseBufferTransition(case_key="case", value="route")
    transition.install()

    with pytest.raises(NodeException, match="No parent"):
        transition.check()
