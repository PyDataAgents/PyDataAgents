from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import shutil
import time
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from pydag.adapters.Adapter import Adapter
from pydag.agents.Agent import Agent
from pydag.agents.AgentElement import (
    AgentElement,
    artifact_descriptor_field,
    persisted_field,
    runtime_handle_field,
)
from pydag.agents.AgentStates import AgentLifecycleState
from pydag.agents.RuntimeStorage import CheckpointReason, CleanupScope
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.Action import Action
from pydag.services.Service import Service
from pydag.services.rest.AgentRESTAPI import AgentRESTAPI
from pydag.services.statemachine.StatemachineService import StatemachineService


def _cleanup_agent_runtime(agent: Agent):
    shutil.rmtree(agent._runtime_storage.runtime_root, ignore_errors=True)


def _workspace_test_path(name: str) -> Path:
    path = Path("resources") / "tmp-tests" / "agent" / name / uuid.uuid4().hex[:8]
    path.mkdir(parents=True, exist_ok=True)
    return path


def _wait_until(predicate, timeout: float = 2.0, interval: float = 0.05):
    end = time.time() + timeout
    while time.time() < end:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()


class DummyAdapter(Adapter):
    def __post_init__(self):
        super().__post_init__()
        self.install_calls = 0
        self.uninstall_calls = 0
        self.connect_calls = 0
        self.disconnect_calls = 0

    def _on_install(self, agent=None):
        self.install_calls += 1

    def _on_uninstall(self, agent=None):
        self.uninstall_calls += 1

    def _on_connect(self) -> bool:
        self.connect_calls += 1
        return True

    def _on_disconnect(self) -> bool:
        self.disconnect_calls += 1
        return True


@dataclass
class DummyService(Service):
    auto_start: bool = field(default=True)

    def __post_init__(self):
        super().__post_init__()
        self.install_calls = 0
        self.uninstall_calls = 0
        self.start_calls = 0
        self.stop_calls = 0
        self.pause_calls = 0
        self.resume_calls = 0
        self.quiesce_calls = 0

    def _on_install(self, agent=None):
        super()._on_install(agent)
        self.install_calls += 1

    def _on_uninstall(self, agent=None):
        self.uninstall_calls += 1
        super()._on_uninstall(agent)

    def _on_start(self):
        self.start_calls += 1

    def _on_stop(self):
        self.stop_calls += 1

    def pause(self):
        self.pause_calls += 1
        super().pause()

    def resume(self):
        self.resume_calls += 1
        super().resume()

    def quiesce(self):
        self.quiesce_calls += 1
        super().quiesce()


class DummyAction(Action):
    def __post_init__(self):
        super().__post_init__()
        self.execute_calls = 0

    def _on_execute(self):
        self.execute_calls += 1


@dataclass
class DummyStatemachineService(StatemachineService):
    def __post_init__(self):
        super().__post_init__()


@dataclass
class DeclarativeElement(AgentElement):
    label: str = field(default="demo", metadata={"description": "demo label"})
    _counter: int = persisted_field(default=0, init=False, repr=False)
    _artifact_path: str | None = artifact_descriptor_field(default=None, init=False, repr=False, name="demo-artifact")
    _runtime_handle: dict | None = runtime_handle_field(default=None, init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()
        self._runtime_handle = {"created": True}

    def _on_install(self, agent=None):
        return

    def _on_uninstall(self, agent=None):
        self._runtime_handle = None

    def rebuild_runtime_handles(self, agent=None):
        self._runtime_handle = {"rebuilt": True}


@dataclass
class InvalidDeclarativeElement(AgentElement):
    label: str = field(default="invalid", metadata={"description": "invalid"})
    _missing_role: int = field(default=0, init=False, repr=False)

    def _on_install(self, agent=None):
        return

    def _on_uninstall(self, agent=None):
        return


def test_agent_get_buffer_returns_none_for_missing_id():
    agent = Agent()
    buffer = DictBuffer(id="BUF1")
    agent.add_buffer(buffer)

    try:
        assert agent.get_buffer("BUF2") is None
    finally:
        _cleanup_agent_runtime(agent)


def test_agent_get_buffer_returns_registered_buffer():
    agent = Agent()
    buffer = DictBuffer(id="BUF1")
    agent.add_buffer(buffer)

    try:
        assert agent.get_buffer("BUF1") is buffer
    finally:
        _cleanup_agent_runtime(agent)


def test_agent_get_lifecycle_state_and_internal_setter_update_runtime_state():
    agent = Agent(id="AG_STATE")

    try:
        assert agent.get_lifecycle_state() == AgentLifecycleState.CREATED
        agent._set_lifecycle_state(AgentLifecycleState.PAUSED)
        assert agent.get_lifecycle_state() == AgentLifecycleState.PAUSED
        assert agent._runtime_storage.get_lifecycle_state() == AgentLifecycleState.PAUSED.value
    finally:
        _cleanup_agent_runtime(agent)


def test_agent_save_and_load_config_roundtrip_for_default_and_custom_paths():
    agent = Agent(id="AG_CONFIG", description="before")
    buffer = DictBuffer(id="BUF_CONFIG")
    agent.add_buffer(buffer)
    custom_dir = _workspace_test_path("config-roundtrip")
    custom_path = custom_dir / "agent.json"

    try:
        default_path = agent.save_config()
        assert default_path.exists()
        assert agent.save_config(custom_path) == custom_path
        assert custom_path.exists()

        agent.description = "changed"
        agent.buffer_store = {}
        assert agent.load_config(custom_path) is True
        assert agent.description == "before"
        assert "BUF_CONFIG" in agent.buffer_store

        agent.description = "changed-again"
        assert agent.load_config() is True
        assert agent.description == "before"

        saved_payload = json.loads(custom_path.read_text(encoding="utf-8"))
        assert saved_payload["id"] == "AG_CONFIG"
        assert saved_payload["uid"] == agent.uid
    finally:
        _cleanup_agent_runtime(agent)
        shutil.rmtree(custom_dir, ignore_errors=True)


def test_agent_load_config_returns_false_for_missing_file():
    agent = Agent(id="AG_NO_CONFIG")
    missing = _workspace_test_path("missing-config") / "missing.json"

    try:
        assert agent.load_config(missing) is False
    finally:
        _cleanup_agent_runtime(agent)
        shutil.rmtree(missing.parent, ignore_errors=True)


def test_agent_element_declarative_persistence_roundtrip_restores_inline_and_artifact_state():
    agent = Agent(id="AG_DECLARATIVE")
    element = DeclarativeElement(id="DECL")
    artifact_dir = _workspace_test_path("declarative-artifact")

    try:
        element.install(agent)
        element._counter = 5
        element._artifact_path = str(artifact_dir)
        snapshot = element.checkpoint(agent=agent).to_dict()

        clone = DeclarativeElement(id="DECL", uid=element.uid)
        clone.install(agent)
        assert clone.restore(snapshot=snapshot, agent=agent) is True

        assert clone._counter == 5
        assert clone._artifact_path == str(artifact_dir)
        assert clone._runtime_handle == {"rebuilt": True}
        assert "_counter" in snapshot["payload"]
        assert "_runtime_handle" not in snapshot["payload"]
        assert any(item["path"] == str(artifact_dir) for item in snapshot["artifacts"])
    finally:
        element.uninstall(agent)
        if "clone" in locals():
            clone.uninstall(agent)
        _cleanup_agent_runtime(agent)
        shutil.rmtree(artifact_dir, ignore_errors=True)


def test_agent_element_validation_rejects_runtime_dataclass_fields_without_persistence_role():
    with pytest.raises(ValueError, match="without persistence roles"):
        InvalidDeclarativeElement()


def test_agent_get_all_elements_includes_nested_statemachine_nodes():
    agent = Agent(id="AG_ELEMENTS")
    adapter = DummyAdapter(id="ADAPTER_ELEMENTS")
    buffer = DictBuffer(id="BUFFER_ELEMENTS")
    node = DummyAction(id="NODE_ELEMENTS")
    service = DummyStatemachineService(id="SERVICE_ELEMENTS", nodes={node.id: node})

    agent.add_adapter(adapter)
    agent.add_buffer(buffer)
    agent.add_service(service)

    try:
        elements = agent.get_all_elements()
        ids = {element.id for element in elements}
        assert ids == {"ADAPTER_ELEMENTS", "BUFFER_ELEMENTS", "SERVICE_ELEMENTS", "NODE_ELEMENTS"}
    finally:
        _cleanup_agent_runtime(agent)


def test_agent_release_derives_deterministic_agent_and_element_uids():
    agent = Agent(id="Agent Main")
    buffer = DictBuffer(id="Buffer Main")
    service = DummyStatemachineService(id="Service Main", auto_start=False)
    node = DummyAction(id="Node Main")
    service.add_node(node)
    agent.add_buffer(buffer)
    agent.add_service(service)

    try:
        agent.release(blocking=False)

        assert agent.uid == "agent-main"
        assert buffer.uid == "buffer/buffer-main"
        assert service.uid == "service/service-main"
        assert node.uid == "service/service-main/node/node-main"
    finally:
        if agent.is_running():
            agent.terminate()
        _cleanup_agent_runtime(agent)


def test_agent_release_keeps_explicit_uids():
    agent = Agent(id="Agent Explicit", uid="agent/custom")
    buffer = DictBuffer(id="Buffer Explicit", uid="buffer/custom")
    agent.add_buffer(buffer)

    try:
        agent.release(blocking=False)

        assert agent.uid == "agent/custom"
        assert buffer.uid == "buffer/custom"
    finally:
        if agent.is_running():
            agent.terminate()
        _cleanup_agent_runtime(agent)


def test_agent_pause_resume_and_quiesce_are_noops_when_not_running():
    agent = Agent(id="AG_NOOP")

    try:
        agent.pause()
        agent.resume()
        agent.quiesce()

        assert agent.get_lifecycle_state() == AgentLifecycleState.CREATED
        assert agent.is_running() is False
    finally:
        _cleanup_agent_runtime(agent)


def test_agent_release_pause_resume_quiesce_and_terminate_delegate_to_elements():
    agent = Agent(id="AG_LIFECYCLE")
    adapter = DummyAdapter(id="ADAPTER_LIFECYCLE")
    service = DummyService(id="SERVICE_LIFECYCLE")

    agent.add_adapter(adapter)
    agent.add_service(service)

    try:
        agent.release(blocking=False)

        assert agent.is_running() is True
        assert agent.get_lifecycle_state() == AgentLifecycleState.RUNNING
        assert agent._run_id is not None
        assert adapter.install_calls == 1
        assert adapter.connect_calls == 1
        assert service.install_calls == 1
        assert service.start_calls == 1

        agent.pause()
        assert agent.get_lifecycle_state() == AgentLifecycleState.PAUSED
        assert service.pause_calls == 1

        agent.resume()
        assert agent.get_lifecycle_state() == AgentLifecycleState.RUNNING
        assert service.resume_calls == 1

        agent.quiesce()
        assert agent.get_lifecycle_state() == AgentLifecycleState.QUIESCING
        assert service.quiesce_calls == 1

        agent.terminate()
        assert agent.is_running() is False
        assert agent.get_lifecycle_state() == AgentLifecycleState.STOPPED
        assert adapter.disconnect_calls == 1
        assert adapter.uninstall_calls == 1
        assert service.stop_calls == 1
        assert service.uninstall_calls == 1
        assert agent._run_id is None
    finally:
        if agent.is_running():
            agent.terminate()
        _cleanup_agent_runtime(agent)


def test_agent_checkpoint_and_restore_roundtrip_buffer_state_uses_current_checkpoint_by_default():
    agent = Agent(id="AG_RUNTIME")
    buffer = DictBuffer(id="BUF_RUNTIME", timestamps_enabled=True, index_enabled=True)
    agent.add_buffer(buffer)

    try:
        agent.release(blocking=False)
        buffer.push({"value": [1, 2], "label": ["a", "b"]})

        manifest = agent.checkpoint()
        buffer.clear()

        assert agent.restore() is True

        restored = buffer.data()
        assert restored["value"] == [1, 2]
        assert restored["label"] == ["a", "b"]
        assert manifest["checkpoint_id"] == agent._runtime_storage.get_current_checkpoint()
        assert (agent._runtime_storage.manifest_path(manifest["checkpoint_id"])).exists()
    finally:
        if agent.is_running():
            agent.terminate()
        _cleanup_agent_runtime(agent)


def test_agent_release_auto_resumes_exact_match_checkpoint_on_second_run():
    agent1 = Agent(
        id="AG_AUTO_RESUME",
        auto_checkpoint_on_terminate=False,
        auto_checkpoint_interval_seconds=999.0,
    )
    buffer1 = DictBuffer(id="BUF_AUTO_RESUME")
    agent1.add_buffer(buffer1)

    try:
        agent1.release(blocking=False)
        buffer1.push({"value": [1, 2], "label": ["a", "b"]})
        manifest = agent1.checkpoint()
        agent1.terminate()

        agent2 = Agent(
            id="AG_AUTO_RESUME",
            auto_checkpoint_on_terminate=False,
            auto_checkpoint_interval_seconds=999.0,
        )
        buffer2 = DictBuffer(id="BUF_AUTO_RESUME")
        agent2.add_buffer(buffer2)
        agent2.release(blocking=False)

        assert buffer2.data()["value"] == [1, 2]
        report = agent2.status()["last_reconciliation_report"]
        assert report["checkpoint_id"] == manifest["checkpoint_id"]
        assert any(item["uid"] == buffer2.uid for item in report["restored"])
        assert report["fresh_started"] == []
        assert report["removed_ignored"] == []
    finally:
        if agent1.is_running():
            agent1.terminate()
        if "agent2" in locals() and agent2.is_running():
            agent2.terminate()
        _cleanup_agent_runtime(agent1)


def test_agent_release_restores_unchanged_elements_and_fresh_starts_added_elements():
    agent1 = Agent(id="AG_ADDED")
    restored_buffer_1 = DictBuffer(id="BUF_EXISTING")
    agent1.add_buffer(restored_buffer_1)

    try:
        agent1.release(blocking=False)
        restored_buffer_1.push({"value": [11]})
        agent1.checkpoint()
        agent1.terminate()

        agent2 = Agent(id="AG_ADDED")
        restored_buffer_2 = DictBuffer(id="BUF_EXISTING")
        added_buffer = DictBuffer(id="BUF_NEW")
        agent2.add_buffer(restored_buffer_2)
        agent2.add_buffer(added_buffer)
        agent2.release(blocking=False)

        assert restored_buffer_2.data()["value"] == [11]
        assert added_buffer.size() == 0
        report = agent2.status()["last_reconciliation_report"]
        assert any(item["uid"] == restored_buffer_2.uid for item in report["restored"])
        assert any(item["uid"] == added_buffer.uid for item in report["fresh_started"])
    finally:
        if agent1.is_running():
            agent1.terminate()
        if "agent2" in locals() and agent2.is_running():
            agent2.terminate()
        _cleanup_agent_runtime(agent1)


def test_agent_release_ignores_removed_elements_from_old_checkpoint():
    agent1 = Agent(id="AG_REMOVED")
    kept_buffer_1 = DictBuffer(id="BUF_KEPT")
    removed_buffer_1 = DictBuffer(id="BUF_REMOVED")
    agent1.add_buffer(kept_buffer_1)
    agent1.add_buffer(removed_buffer_1)

    try:
        agent1.release(blocking=False)
        kept_buffer_1.push({"value": [21]})
        removed_buffer_1.push({"value": [99]})
        agent1.checkpoint()
        removed_uid = removed_buffer_1.uid
        agent1.terminate()

        agent2 = Agent(id="AG_REMOVED")
        kept_buffer_2 = DictBuffer(id="BUF_KEPT")
        agent2.add_buffer(kept_buffer_2)
        agent2.release(blocking=False)

        assert kept_buffer_2.data()["value"] == [21]
        report = agent2.status()["last_reconciliation_report"]
        assert any(item["uid"] == kept_buffer_2.uid for item in report["restored"])
        assert any(item["uid"] == removed_uid for item in report["removed_ignored"])
    finally:
        if agent1.is_running():
            agent1.terminate()
        if "agent2" in locals() and agent2.is_running():
            agent2.terminate()
        _cleanup_agent_runtime(agent1)


def test_agent_release_fresh_starts_changed_elements_when_definition_changes():
    agent1 = Agent(id="AG_CHANGED")
    buffer1 = DictBuffer(id="BUF_CHANGED", capacity=10)
    agent1.add_buffer(buffer1)

    try:
        agent1.release(blocking=False)
        buffer1.push({"value": [42]})
        agent1.checkpoint()
        agent1.terminate()

        agent2 = Agent(id="AG_CHANGED")
        buffer2 = DictBuffer(id="BUF_CHANGED", capacity=20)
        agent2.add_buffer(buffer2)
        agent2.release(blocking=False)

        assert buffer2.size() == 0
        report = agent2.status()["last_reconciliation_report"]
        assert any(item["uid"] == buffer2.uid for item in report["fresh_started"])
        assert report["restored"] == []
    finally:
        if agent1.is_running():
            agent1.terminate()
        if "agent2" in locals() and agent2.is_running():
            agent2.terminate()
        _cleanup_agent_runtime(agent1)


def test_agent_release_fresh_starts_nodes_when_topology_changes():
    agent1 = Agent(id="AG_TOPO")
    node_a_1 = DummyAction(id="NODE_A", child_ids=["NODE_B"])
    node_b_1 = DummyAction(id="NODE_B")
    service1 = DummyStatemachineService(
        id="SM_TOPO",
        auto_start=False,
        nodes={node_a_1.id: node_a_1, node_b_1.id: node_b_1},
    )
    agent1.add_service(service1)

    try:
        agent1.release(blocking=False)
        node_b_1.execute()
        assert node_b_1.get_last_timestamp() > 0
        agent1.checkpoint()
        node_b_uid = node_b_1.uid
        agent1.terminate()

        agent2 = Agent(id="AG_TOPO")
        node_a_2 = DummyAction(id="NODE_A", child_ids=[])
        node_b_2 = DummyAction(id="NODE_B")
        service2 = DummyStatemachineService(
            id="SM_TOPO",
            auto_start=False,
            nodes={node_a_2.id: node_a_2, node_b_2.id: node_b_2},
        )
        agent2.add_service(service2)
        agent2.release(blocking=False)

        assert node_b_2.get_last_timestamp() == 0
        report = agent2.status()["last_reconciliation_report"]
        assert any(item["uid"] == node_b_uid for item in report["fresh_started"])
        assert any(item["uid"] == service2.uid for item in report["fresh_started"])
    finally:
        if agent1.is_running():
            agent1.terminate()
        if "agent2" in locals() and agent2.is_running():
            agent2.terminate()
        _cleanup_agent_runtime(agent1)


def test_agent_restore_returns_false_when_checkpoint_is_missing():
    agent = Agent(id="AG_RESTORE_MISSING")

    try:
        assert agent.restore("does-not-exist") is False
        assert agent.restore() is False
    finally:
        _cleanup_agent_runtime(agent)


def test_agent_reload_current_creates_new_checkpoint_and_restores_state():
    agent = Agent(id="AG_RELOAD")
    buffer = DictBuffer(id="BUF_RELOAD")
    agent.add_buffer(buffer)

    try:
        agent.release(blocking=False)
        buffer.push({"value": [7, 8]})

        assert agent.reload_current() is True

        current_checkpoint = agent._runtime_storage.get_current_checkpoint()
        assert current_checkpoint is not None
        assert buffer.data()["value"] == [7, 8]
    finally:
        if agent.is_running():
            agent.terminate()
        _cleanup_agent_runtime(agent)


def test_agent_auto_checkpoint_timer_creates_checkpoint_without_change_tracking():
    agent = Agent(
        id=f"AG_TIMER_CP_{uuid.uuid4().hex[:8]}",
        auto_checkpoint_interval_seconds=0.2,
        auto_checkpoint_min_seconds_between_checkpoints=0.0,
    )
    buffer = DictBuffer(id="BUF_TIMER_CP")
    agent.add_buffer(buffer)

    try:
        agent.release(blocking=False)
        assert agent._runtime_storage.get_current_checkpoint() is None

        assert _wait_until(lambda: agent._runtime_storage.get_current_checkpoint() is not None, timeout=2.0)
        assert _wait_until(lambda: agent.status()["last_checkpoint_reason"] == CheckpointReason.AUTO_TIMER.value, timeout=2.0)
        assert agent.status()["last_checkpoint_reason"] == CheckpointReason.AUTO_TIMER.value
    finally:
        if agent.is_running():
            agent.terminate()
        _cleanup_agent_runtime(agent)


def test_agent_terminate_creates_checkpoint_when_configured():
    agent = Agent(
        id="AG_TERM_CP",
        auto_checkpoint_interval_seconds=999.0,
        auto_checkpoint_min_seconds_between_checkpoints=0.0,
    )
    buffer = DictBuffer(id="BUF_TERM_CP")
    agent.add_buffer(buffer)

    try:
        agent.release(blocking=False)
        buffer.push({"value": [7]})
        agent.terminate()

        assert agent._runtime_storage.get_current_checkpoint() is not None
        assert agent._runtime_storage.get_runtime_value("last_checkpoint_reason") == CheckpointReason.TERMINATE.value
    finally:
        if agent.is_running():
            agent.terminate()
        _cleanup_agent_runtime(agent)


def test_agent_failed_checkpoint_keeps_previous_current_checkpoint_pointer():
    agent = Agent(id="AG_CP_FAIL")
    buffer = DictBuffer(id="BUF_CP_FAIL")
    agent.add_buffer(buffer)

    try:
        agent.release(blocking=False)
        buffer.push({"value": [1]})
        first_manifest = agent.checkpoint()
        current_checkpoint = agent._runtime_storage.get_current_checkpoint()
        original_write_manifest = agent._runtime_storage.write_manifest

        def _failing_write_manifest(manifest):
            raise RuntimeError("simulated-manifest-failure")

        agent._runtime_storage.write_manifest = _failing_write_manifest
        buffer.push({"value": [2]})

        with pytest.raises(RuntimeError, match="simulated-manifest-failure"):
            agent.checkpoint(checkpoint_reason=CheckpointReason.MANUAL.value)

        assert agent._runtime_storage.get_current_checkpoint() == current_checkpoint == first_manifest["checkpoint_id"]
        assert agent.status()["last_checkpoint_success"] is False
    finally:
        if "original_write_manifest" in locals():
            agent._runtime_storage.write_manifest = original_write_manifest
        if agent.is_running():
            agent.terminate()
        _cleanup_agent_runtime(agent)


def test_agent_restart_after_failed_checkpoint_uses_prior_valid_checkpoint():
    agent1 = Agent(
        id="AG_RESTART_CP_FAIL",
        auto_checkpoint_on_terminate=False,
        auto_checkpoint_interval_seconds=999.0,
    )
    buffer1 = DictBuffer(id="BUF_RESTART_CP_FAIL")
    agent1.add_buffer(buffer1)

    try:
        agent1.release(blocking=False)
        buffer1.push({"value": [1], "label": ["ok"]})
        first_manifest = agent1.checkpoint()
        original_write_manifest = agent1._runtime_storage.write_manifest

        def _failing_write_manifest(manifest):
            raise RuntimeError("simulated-manifest-failure")

        agent1._runtime_storage.write_manifest = _failing_write_manifest
        buffer1.push({"value": [2], "label": ["new"]})

        with pytest.raises(RuntimeError, match="simulated-manifest-failure"):
            agent1.checkpoint(checkpoint_reason=CheckpointReason.MANUAL.value)

        agent1._runtime_storage.write_manifest = original_write_manifest
        agent1.terminate()

        agent2 = Agent(
            id="AG_RESTART_CP_FAIL",
            auto_checkpoint_on_terminate=False,
            auto_checkpoint_interval_seconds=999.0,
        )
        buffer2 = DictBuffer(id="BUF_RESTART_CP_FAIL")
        agent2.add_buffer(buffer2)
        agent2.release(blocking=False)

        restored = buffer2.data()
        report = agent2.status()["last_reconciliation_report"]

        assert restored["value"] == [1]
        assert restored["label"] == ["ok"]
        assert report["checkpoint_id"] == first_manifest["checkpoint_id"]
        assert any(item["uid"] == buffer2.uid for item in report["restored"])
    finally:
        if "original_write_manifest" in locals():
            agent1._runtime_storage.write_manifest = original_write_manifest
        if agent1.is_running():
            agent1.terminate()
        if "agent2" in locals() and agent2.is_running():
            agent2.terminate()
        _cleanup_agent_runtime(agent1)


def test_agent_cleanup_tmp_only_supports_dry_run_and_delete():
    agent = Agent(id="AG_TMP_CLEAN")
    tmp_file = agent._runtime_storage.tmp_root / "temp.txt"
    tmp_dir = agent._runtime_storage.tmp_root / "temp-dir"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_file.write_text("tmp", encoding="utf-8")
    (tmp_dir / "nested.txt").write_text("nested", encoding="utf-8")

    try:
        dry_run = agent.cleanup(scope=CleanupScope.TMP_ONLY.value, dry_run=True)
        assert tmp_file.exists()
        assert tmp_dir.exists()
        assert str(tmp_file) in dry_run["candidates"]
        assert str(tmp_dir) in dry_run["candidates"]

        report = agent.cleanup(scope=CleanupScope.TMP_ONLY.value, dry_run=False)
        assert not tmp_file.exists()
        assert not tmp_dir.exists()
        assert str(tmp_file) in report["deleted"]
        assert str(tmp_dir) in report["deleted"]
    finally:
        _cleanup_agent_runtime(agent)


def test_agent_cleanup_checkpoint_pruning_keeps_current_checkpoint_when_keep_last_is_zero():
    agent = Agent(id="AG_CLEANUP")
    buffer = DictBuffer(id="BUF_CLEANUP")
    agent.add_buffer(buffer)

    try:
        agent.release(blocking=False)
        checkpoint_ids = []
        for idx in range(3):
            buffer.push({"value": [idx]})
            checkpoint_ids.append(agent.checkpoint()["checkpoint_id"])
            time.sleep(0.01)

        report = agent.cleanup(
            scope=CleanupScope.CHECKPOINT_RETENTION_PRUNING.value,
            dry_run=False,
            keep_last_n_checkpoints=0,
        )
        remaining = sorted(path.name for path in agent._runtime_storage.checkpoints_root.iterdir() if path.is_dir())

        assert remaining == [checkpoint_ids[-1]]
        assert checkpoint_ids[-1] in report["skipped"]
        assert any(checkpoint_ids[0] in deleted for deleted in report["deleted"])
    finally:
        if agent.is_running():
            agent.terminate()
        _cleanup_agent_runtime(agent)


def test_agent_status_reports_runtime_summary():
    agent = Agent(id="AG_STATUS")
    adapter = DummyAdapter(id="ADAPTER_STATUS")
    buffer = DictBuffer(id="BUFFER_STATUS")
    service = DummyService(id="SERVICE_STATUS")
    agent.add_adapter(adapter)
    agent.add_buffer(buffer)
    agent.add_service(service)

    try:
        agent.release(blocking=False)
        status = agent.status()

        assert status["id"] == "AG_STATUS"
        assert status["uid"] == agent.uid
        assert status["is_running"] is True
        assert status["lifecycle_state"] == AgentLifecycleState.RUNNING.value
        assert status["run_id"] == agent._run_id
        assert status["resume_mode"] == agent.resume_mode
        assert status["auto_checkpoint_config"]["resume_mode"] == agent.resume_mode
        assert "last_reconciliation_report" in status
        assert "BUFFER_STATUS" in status["buffers"]
        assert "ADAPTER_STATUS" in status["adapters"]
        assert "SERVICE_STATUS" in status["services"]
    finally:
        if agent.is_running():
            agent.terminate()
        _cleanup_agent_runtime(agent)


def test_agent_rest_api_exposes_runtime_control_endpoints():
    agent = Agent(id="AG_REST")
    buffer = DictBuffer(id="BUF_REST")
    agent.add_buffer(buffer)
    app = FastAPI()
    app.include_router(AgentRESTAPI.get_api_router(agent))
    client = TestClient(app)

    try:
        agent.release(blocking=False)
        buffer.push({"value": [1]})

        status_response = client.get("/api/v1/agent/status")
        checkpoint_response = client.post("/api/v1/agent/checkpoint")
        pause_response = client.post("/api/v1/agent/pause")
        resume_response = client.post("/api/v1/agent/resume")
        cleanup_response = client.post(
            "/api/v1/agent/cleanup",
            json={"scope": CleanupScope.TMP_ONLY.value, "dry_run": True},
        )

        assert status_response.status_code == 200
        assert status_response.json()["id"] == "AG_REST"
        assert checkpoint_response.status_code == 200
        assert checkpoint_response.json()["success"] is True
        assert pause_response.status_code == 200
        assert pause_response.json()["success"] is True
        assert resume_response.status_code == 200
        assert resume_response.json()["success"] is True
        assert cleanup_response.status_code == 200
        assert cleanup_response.json()["cleanup"]["scope"] == CleanupScope.TMP_ONLY.value
    finally:
        client.close()
        if agent.is_running():
            agent.terminate()
        _cleanup_agent_runtime(agent)
