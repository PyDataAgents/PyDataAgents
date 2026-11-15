from pydag.agents.AgentStates import ServiceState
from pydag.nodes.Action import Action
from pydag.nodes.utils.FalseTransition import FalseTransition
from pydag.nodes.utils.PrintAction import PrintAction
from pydag.nodes.utils.SleepAction import SleepAction
from pydag.nodes.utils.TrueTransition import TrueTransition
from pydag.services.ThreadType import ThreadType
from pydag.services.statemachine.SimpleStatemachine import SimpleStatemachine


class RecordingAction(Action):
    def __init__(self, label: str, events: list[str], **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.events = events

    def _on_execute(self):
        self.events.append(self.label)


def _run_once(service: SimpleStatemachine):
    service.start()
    service._thread.join(timeout=2)

    assert service._thread.is_alive() is False
    assert service.get_state() == ServiceState.INSTALLED


def test_executes_active_actions_once_in_node_order():
    events = []
    first = RecordingAction("first", events, id="first")
    inactive = RecordingAction("inactive", events, id="inactive")
    second = RecordingAction("second", events, id="second")
    inactive.set_active(False)

    service = SimpleStatemachine(thread_type=ThreadType.ONLY_ONCE.value)
    service.add_node(first)
    service.add_node(inactive)
    service.add_node(second)
    service.install()

    _run_once(service)

    assert events == ["first", "second"]


def test_true_transition_continues_to_later_nodes():
    events = []
    before = RecordingAction("before", events, id="before")
    transition = TrueTransition(id="transition")
    after = RecordingAction("after", events, id="after")

    service = SimpleStatemachine(thread_type=ThreadType.ONLY_ONCE.value)
    service.add_node(before)
    service.add_node(transition)
    service.add_node(after)
    service.install()

    _run_once(service)

    assert events == ["before", "after"]


def test_false_transition_stops_current_observer_pass():
    events = []
    before = RecordingAction("before", events, id="before")
    transition = FalseTransition(id="transition")
    after = RecordingAction("after", events, id="after")

    service = SimpleStatemachine(thread_type=ThreadType.ONLY_ONCE.value)
    service.add_node(before)
    service.add_node(transition)
    service.add_node(after)
    service.install()

    _run_once(service)

    assert events == ["before"]
    
def test_simple_statemachine_install():
    ssm = SimpleStatemachine(thread_type=ThreadType.ONLY_ONCE.value)
    
    pa1 = PrintAction("pa1", id="pa1", child_ids=["pa2"])
    pa2 = PrintAction("pa2", id="pa2", child_ids=["sa1"])
    sa1 = SleepAction(0.5, id="sa1")
    
    ssm.add_node(pa1)
    ssm.add_node(pa2)
    ssm.add_node(sa1)
    
    ssm.install()
    
    assert len(sa1.get_parents()) > 0, "SleepAction should have parents after installation"
    
    
