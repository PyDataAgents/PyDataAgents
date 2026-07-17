from pydag.agents.AgentStates import ServiceState
from pydag.nodes.Action import Action
from pydag.nodes.utils.CountAction import CountAction
from pydag.nodes.utils.CountTransition import CountTransition
from pydag.nodes.utils.JoinTransition import JoinTransition
from pydag.nodes.utils.StartAction import StartAction
from pydag.nodes.utils.StopAction import StopAction
from pydag.nodes.utils.TrueTransition import TrueTransition
from pydag.services.ThreadType import ThreadType
from pydag.services.statemachine.SFCService import SFCService


class DeactivateAction(Action):
    def _on_execute(self):
        self.set_active(False)


def _run_service_to_completion(service: SFCService):
    service.start()
    service._thread.join(timeout=2)

    assert service._thread.is_alive() is False
    assert service.get_state() == ServiceState.INSTALLED


def test_install_deduplicates_revisited_transitions():
    first = TrueTransition(id="first")
    second = TrueTransition(id="second")
    first.add_child(second)
    second.add_child(first)

    service = SFCService()
    service.add_node(first)
    service.add_node(second)

    service.install()

    assert service.get_transitions() == {
        "first": first,
        "second": second,
    }
    assert first.is_active() is False
    assert second.is_active() is False


def test_executes_action_until_transition_condition_is_met():
    start = StartAction(id="start")
    counter = CountAction(id="counter")
    transition = CountTransition(counter)
    transition.id = "transition"
    transition.trigger_count = 3
    stop = StopAction(id="stop")

    start.add_child(counter)
    counter.add_child(transition)
    transition.add_child(stop)

    service = SFCService(thread_type=ThreadType.ONLY_ONCE.value)
    service.add_node(start)
    service.add_node(counter)
    service.add_node(transition)
    service.add_node(stop)
    service.install()

    _run_service_to_completion(service)

    assert counter.count == 3
    assert service.has_active_actions() is False
    assert service.has_active_transitions() is False


def test_join_transition_waits_for_all_parent_actions():
    start = StartAction(id="start")
    left = CountAction(id="left")
    right = CountAction(id="right")
    join = JoinTransition(id="join")
    after_join = CountAction(id="after_join")
    stop = StopAction(id="stop")

    start.add_child(left)
    start.add_child(right)
    left.add_child(join)
    right.add_child(join)
    join.add_child(after_join)
    after_join.add_child(stop)

    service = SFCService(thread_type=ThreadType.ONLY_ONCE.value)
    service.add_node(start)
    service.add_node(left)
    service.add_node(right)
    service.add_node(join)
    service.add_node(after_join)
    service.add_node(stop)
    service.install()

    _run_service_to_completion(service)

    assert left.count == 1
    assert right.count == 1
    assert after_join.count == 1
    assert join.visited_from_parents == {}


def test_direct_action_chain_runs_before_transition_boundary():
    start = StartAction(id="start")
    first = CountAction(id="first")
    second = CountAction(id="second")
    transition = CountTransition(second)
    transition.id = "transition"
    transition.trigger_count = 1
    stop = StopAction(id="stop")

    start.add_child(first)
    first.add_child(second)
    second.add_child(transition)
    transition.add_child(stop)

    service = SFCService(thread_type=ThreadType.ONLY_ONCE.value)
    service.add_node(start)
    service.add_node(first)
    service.add_node(second)
    service.add_node(transition)
    service.add_node(stop)
    service.install()

    _run_service_to_completion(service)

    assert first.count == 1
    assert second.count == 1


def test_transition_loop_runs_until_exit_transition_is_met():
    start = StartAction(id="start")
    counter = CountAction(id="counter")
    loop = CountTransition(counter)
    loop.id = "loop"
    loop.negate = True
    loop.trigger_count = 3
    exit_transition = CountTransition(counter)
    exit_transition.id = "exit"
    exit_transition.trigger_count = 3
    stop = DeactivateAction(id="stop")

    start.add_child(counter)
    counter.add_child(loop)
    counter.add_child(exit_transition)
    loop.add_child(counter)
    exit_transition.add_child(stop)

    service = SFCService(thread_type=ThreadType.ONLY_ONCE.value)
    service.add_node(start)
    service.add_node(counter)
    service.add_node(loop)
    service.add_node(exit_transition)
    service.add_node(stop)
    service.install()

    _run_service_to_completion(service)

    assert counter.count == 3
    assert service.has_active_actions() is False
    assert service.has_active_transitions() is False


def test_remove_node_clears_assembled_action_and_transition_caches():
    start = StartAction(id="start")
    counter = CountAction(id="counter")
    transition = CountTransition(counter)
    transition.id = "transition"

    start.add_child(counter)
    counter.add_child(transition)

    service = SFCService()
    service.add_node(start)
    service.add_node(counter)
    service.add_node(transition)
    service.install()

    service.remove_node("counter")
    service.remove_node("transition")

    assert "counter" not in service.nodes
    assert "counter" not in service.get_actions()
    assert "transition" not in service.nodes
    assert "transition" not in service.get_transitions()
