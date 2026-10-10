import os
from unittest.mock import Mock

import pytest

from pydag.agents.Agent import Agent
from pydag.agents.AgentStates import AgentElementState, ServiceState
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.documents.CopyFilesAction import CopyFilesAction
from pydag.nodes.documents.ListFilesAction import ListFilesAction
from pydag.services.Service import Service
from pydag.services.ServiceException import ServiceException
from pydag.services.ThreadType import ThreadType
from pydag.services.statemachine.SimpleStatemachine import SimpleStatemachine
from pydag.utils.FileUtils import FileUtils


class ControlledService(Service):
    def _on_start(self):
        pass

    def _on_stop(self):
        pass


@pytest.mark.parametrize("kind", ["empty", "disabled", "finished", "failed"])
def test_release_without_running_services(kind):
    agent = Agent()
    buffer = DictBuffer()
    agent.add_buffer(buffer)
    service = ControlledService(auto_start=kind != "disabled")
    if kind == "finished":
        service._on_start = service.stop
    elif kind == "failed":
        service._on_start = Mock(side_effect=ServiceException("Startup failed"))
    if kind != "empty":
        agent.add_service(service)

    agent.release(stop_when_idle=True)

    assert not agent.is_running()
    assert buffer.get_state() == AgentElementState.UNINSTALLED
    if kind != "empty":
        assert service.get_state() == AgentElementState.UNINSTALLED


def test_release_waits_for_last_service(monkeypatch):
    agent = Agent()
    first, last = ControlledService(), ControlledService()
    agent.add_service(first)
    agent.add_service(last)
    waits = []

    def wait(timeout):
        assert agent.is_running()
        waits.append(timeout)
        if len(waits) == 1:
            first.stop()
        else:
            assert len(waits) == 2
            assert last.get_state() == ServiceState.RUNNING
            last.set_state(AgentElementState.ERROR)
        return False

    monkeypatch.setattr(agent._stop_event, "wait", wait)
    agent.release(stop_when_idle=True)

    assert len(waits) == 2
    assert not agent.is_running()
    assert first.get_state() == last.get_state() == AgentElementState.UNINSTALLED


@pytest.mark.parametrize("blocking", [True, False])
def test_default_release_requires_manual_termination(blocking, monkeypatch):
    agent = Agent()
    wait = Mock(side_effect=agent.terminate)
    monkeypatch.setattr(agent._stop_event, "wait", wait)

    agent.release(blocking=blocking)

    assert agent.is_running() == (not blocking)
    assert wait.call_count == int(blocking)
    agent.terminate()


@pytest.mark.parametrize("manual", [True, False])
def test_nonblocking_release_cleanup_and_restart(manual):
    agent = Agent()
    service = ControlledService()
    agent.add_service(service)
    service._on_uninstall = Mock(wraps=service._on_uninstall)

    for run in range(2):
        agent.release(blocking=False, stop_when_idle=True)
        assert agent.is_running()
        if manual:
            agent.terminate()
        else:
            service.stop()
        assert agent._stop_event.wait(2), "Agent did not terminate"
        assert not agent.is_running()
        assert service.get_state() == AgentElementState.UNINSTALLED
        assert service._on_uninstall.call_count == run + 1


def test_blocking_release_can_be_terminated_manually(monkeypatch):
    agent = Agent()
    agent.add_service(ControlledService())
    monkeypatch.setattr(agent._stop_event, "wait", Mock(side_effect=lambda timeout: agent.terminate()))

    agent.release(stop_when_idle=True)

    assert not agent.is_running()
    
def test_statemachine_release_stop():
    agent = Agent()
    
    sm = SimpleStatemachine(thread_type=ThreadType.ONLY_ONCE.value)
    
    folder = os.path.dirname(__file__)
    la = ListFilesAction(folder=folder)
    sm.add_node(la)
    
    tfolder = FileUtils.user_home() + os.sep + "Downloads" + os.sep + "test_agent_release"
    ca = CopyFilesAction(target_folder=tfolder)
    ca.add_parent(la)
    sm.add_node(ca)
    
    agent.add_service(sm)
    
    agent.release(stop_when_idle=True)
    
    assert len(FileUtils.list_files(tfolder)) > 0
    FileUtils.delete_dir(tfolder)
