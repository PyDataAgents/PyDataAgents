from __future__ import annotations
import json
import threading
import time
from typing import TYPE_CHECKING, Type, cast
from dataclasses import dataclass, field
from pathlib import Path
import uuid
from loguru import logger


from ..nodes.Node import Node
from .AgentElement import AgentElement
from .AgentConfig import AgentConfig
from .AgentStates import AgentLifecycleState
from .RuntimeStorage import (
    AutoCheckpointConfig,
    CheckpointManifest,
    CheckpointReason,
    CleanupReport,
    CleanupScope,
    ElementReconciliationOutcome,
    ElementReconciliationResult,
    ReconciliationReport,
    ResumeMode,
    RuntimeStorage,
    normalize_runtime_key,
    stable_fingerprint,
)
from ..utils.ClassUtils import ClassUtils
from ..utils.FileUtils import FileUtils
from ..utils.TimeUtils import TimeUtils
from ..services.statemachine.StatemachineService import StatemachineService


if TYPE_CHECKING:
    from ..adapters.Adapter import Adapter
    from ..buffers.Buffer import Buffer
    from ..services.Service import Service


@dataclass
class Agent():
    
    id : str = field(default=None, metadata={"description": "unique identifier of the Agent application"})
    description : str = field(default=None, metadata={"description": "application/agent description"})
    buffer_store : dict[str, Buffer] = field(default_factory=dict, metadata={"description": "dictionary of Buffers in the Agent"})
    adapter_store : dict[str, Adapter] = field(default_factory=dict, metadata={"description": "dictionary of Adapters in the Agent"})
    service_store : dict[str, Service] = field(default_factory=dict, metadata={"description": "dictionary of Services in the Agent"})
    uid : str = field(default=None)
    resume_mode : str = field(default=ResumeMode.EXACT_MATCH_ONLY.value, metadata={"description": "startup resume mode for runtime checkpoints"})
    auto_checkpoint_enabled : bool = field(default=True, metadata={"description": "enables periodic automatic checkpoints"})
    auto_checkpoint_interval_seconds : float = field(default=60.0, metadata={"description": "interval between automatic checkpoint attempts in seconds"})
    auto_checkpoint_on_terminate : bool = field(default=True, metadata={"description": "create a checkpoint before graceful termination"})
    auto_checkpoint_on_reload : bool = field(default=True, metadata={"description": "create a checkpoint during reload operations"})
    auto_checkpoint_on_quiesce : bool = field(default=False, metadata={"description": "create a checkpoint when quiesce is requested"})
    auto_checkpoint_min_seconds_between_checkpoints : float = field(default=5.0, metadata={"description": "minimum spacing between automatic checkpoints in seconds"})

    def __post_init__(self):
        """ initialize `Agent` instance after dataclass initialization.
        
        Sets up the internal storage dictionaries for `Buffer`s, `Adapter`s, and `Service`s.
        Generates a unique ID if not provided.
        """
        if self.id is None: 
            self.id = f"{self.__class__.__name__} [{uuid.uuid4()}]"
        self._uid_explicit : bool = self.uid is not None
        if self.uid is None:
            self.uid = self._build_auto_uid()
        self._is_running = False
        self._stop_event = threading.Event()
        self._checkpoint_stop_event = threading.Event()
        self._control_lock = threading.RLock()
        self._checkpoint_lock = threading.RLock()
        self._checkpoint_thread : threading.Thread = None
        self._lifecycle_state = AgentLifecycleState.CREATED
        self._run_id : str = None
        self._auto_checkpoint_config = AutoCheckpointConfig(
            enabled=self.auto_checkpoint_enabled,
            interval_seconds=self.auto_checkpoint_interval_seconds,
            checkpoint_on_terminate=self.auto_checkpoint_on_terminate,
            checkpoint_on_reload=self.auto_checkpoint_on_reload,
            checkpoint_on_quiesce=self.auto_checkpoint_on_quiesce,
            min_seconds_between_checkpoints=self.auto_checkpoint_min_seconds_between_checkpoints,
            resume_mode=self.resume_mode,
        )
        self._last_checkpoint_reason : str | None = None
        self._last_checkpoint_success : bool | None = None
        self._last_checkpoint_error : str | None = None
        self._last_checkpoint_timestamp : int | None = None
        self._last_reconciliation_report : dict = {}
        self._runtime_storage = RuntimeStorage(self.uid)
        self._runtime_storage.ensure_layout()
        if self._runtime_storage.get_lifecycle_state() is None:
            self._runtime_storage.set_lifecycle_state(self._lifecycle_state.value)
        self._load_runtime_metadata()
        self._runtime_storage.set_runtime_value("resume_mode", self.resume_mode)
        self._runtime_storage.set_runtime_value("auto_checkpoint_config", self._auto_checkpoint_config.to_dict())
    
    def _install_elements(self):
        """ install all `Adapter`s, `Buffer`s, and `Service`s in the `Agent`.
        
        iterates over each element and calls its install method with the `Agent` instance.
        """
        # iterating over a list of dictionary items, in case of modification on the dictionary aoccurs during installs
        for adapter in list(self.adapter_store.values()):
            adapter.install(self)
        for buffer in list(self.buffer_store.values()):
            buffer.install(self)
        for service in list(self.service_store.values()):
            service.install(self)
        self._set_lifecycle_state(AgentLifecycleState.READY)
        
    def _uninstall_elements(self):
        """ uninstall all `Adapter`s, `Buffer`s, and `Service`s from the `Agent`.
        
        iterates over each element and calls its uninstall method.
        """
        # iterating over a list of dictionary items, in case of modification on the dictionary aoccurs during uninstalls
        for adapter in list(self.adapter_store.values()):
            adapter.uninstall(self)
        for buffer in list(self.buffer_store.values()):
            buffer.uninstall(self)
        for service in list(self.service_store.values()):
            service.uninstall(self)
        self._set_lifecycle_state(AgentLifecycleState.STOPPED)
    
    def add_buffer(self, buffer : Buffer):
        """Add a `Buffer` to the `Agent`'s buffer store.
        
        Args:
            buffer (Buffer): the Buffer instance to add.
        """
        if buffer.id in self.buffer_store:
            logger.warning(f"A {buffer.__class__.__name__} with id='{buffer.id}' already exists in {self.__class__.__name__}'s buffer_store and is overwritten!")        
        self.buffer_store[buffer.id] = buffer
        # in order to make duplicate buffers and their ids available in agent for later elements or acces (in scripts), we install them right away
        if len(buffer.duplicate_ids) > 0:
            buffer.install(self)
        
    def add_adapter(self, adapter : Adapter):
        """Add an Adapter to the Agent's adapter store.
        
        Args:
            adapter (Adapter): The Adapter instance to add.
        """
        if adapter.id in self.adapter_store:
            logger.warning(f"A {adapter.__class__.__name__} with id='{adapter.id}' already exists in {self.__class__.__name__}'s adapter_store and is overwritten!")
        self.adapter_store[adapter.id] = adapter
        
    def add_service(self, service : Service):
        """Add a Service to the Agent's service store.
        
        Args:
            service (Service): The Service instance to add.
        """
        if service.id in self.service_store:
            logger.warning(f"A {service.__class__.__name__} with id='{service.id}' already exists in {self.__class__.__name__}'s service_store and is overwritten!")
        self.service_store[service.id] = service
           
    def config_options(self, with_descriptions = False) -> dict:
        """ get the configuration options for the whole `Agent`.
        
        Args:
            with_descriptions (bool, optional): Whether to include descriptions. Defaults to False.
        
        Returns:
            dict: Configuration options dictionary.
        """
        return AgentConfig.config_options(self, with_descriptions)

    def _build_auto_uid(self) -> str:
        return normalize_runtime_key(self.id, fallback="agent")

    def _sync_auto_checkpoint_config(self):
        self._auto_checkpoint_config = AutoCheckpointConfig(
            enabled=self.auto_checkpoint_enabled,
            interval_seconds=self.auto_checkpoint_interval_seconds,
            checkpoint_on_terminate=self.auto_checkpoint_on_terminate,
            checkpoint_on_reload=self.auto_checkpoint_on_reload,
            checkpoint_on_quiesce=self.auto_checkpoint_on_quiesce,
            min_seconds_between_checkpoints=self.auto_checkpoint_min_seconds_between_checkpoints,
            resume_mode=self.resume_mode,
        )
        self._runtime_storage.set_runtime_value("resume_mode", self.resume_mode)
        self._runtime_storage.set_runtime_value("auto_checkpoint_config", self._auto_checkpoint_config.to_dict())

    def _ensure_runtime_storage_matches_uid(self):
        if self._runtime_storage.agent_uid != self.uid:
            self._runtime_storage = RuntimeStorage(self.uid)
            self._runtime_storage.ensure_layout()
        else:
            self._runtime_storage.ensure_layout()
        self._load_runtime_metadata()

    def _load_runtime_metadata(self):
        self._last_checkpoint_reason = self._runtime_storage.get_runtime_value("last_checkpoint_reason")
        self._last_checkpoint_success = self._runtime_storage.get_runtime_value("last_checkpoint_success")
        self._last_checkpoint_error = self._runtime_storage.get_runtime_value("last_checkpoint_error")
        self._last_checkpoint_timestamp = self._runtime_storage.get_runtime_value("last_checkpoint_timestamp")
        self._last_reconciliation_report = self._runtime_storage.get_runtime_value("last_reconciliation_report", {}) or {}

    def _finalize_runtime_identities(self):
        if not self._uid_explicit:
            self.uid = self._build_auto_uid()
        self._ensure_runtime_storage_matches_uid()
        for adapter in self.adapter_store.values():
            adapter.refresh_runtime_identity(uid_prefix="adapter")
        for buffer in self.buffer_store.values():
            buffer.refresh_runtime_identity(uid_prefix="buffer")
        for service in self.service_store.values():
            service.refresh_runtime_identity(uid_prefix="service")
            if isinstance(service, StatemachineService):
                for node in service.nodes.values():
                    node.refresh_runtime_identity(uid_prefix="node", owner_scope=service.uid)

    def _iter_elements_with_context(self):
        for adapter in self.adapter_store.values():
            yield adapter, None
        for buffer in self.buffer_store.values():
            yield buffer, None
        for service in self.service_store.values():
            yield service, None
            if isinstance(service, StatemachineService):
                for node in service.nodes.values():
                    yield node, service

    def _element_inventory_record(self, element: AgentElement, owner: AgentElement = None) -> dict:
        config_fingerprint = element.get_config_fingerprint(self)
        topology_fingerprint = element.get_topology_fingerprint(self)
        persistence_schema_fingerprint = element.get_persistence_schema_fingerprint()
        owner_uid = owner.uid if owner is not None else None
        owner_type = owner.type if owner is not None else None
        owner_config_fingerprint = owner.get_config_fingerprint(self) if owner is not None else None
        owner_scope = element.get_owner_scope(self)
        payload = {
            "uid": element.uid,
            "id": element.id,
            "type": element.type,
            "class_name": element.__class__.__name__,
            "config_fingerprint": config_fingerprint,
            "persistence_schema_fingerprint": persistence_schema_fingerprint,
            "owner_uid": owner_uid,
            "owner_type": owner_type,
            "owner_config_fingerprint": owner_config_fingerprint,
            "owner_scope": owner_scope,
            "topology_fingerprint": topology_fingerprint,
        }
        payload["definition_fingerprint"] = stable_fingerprint(payload)
        return payload

    def _build_element_inventory(self) -> dict[str, dict]:
        inventory : dict[str, dict] = {}
        for element, owner in self._iter_elements_with_context():
            inventory[element.uid] = self._element_inventory_record(element, owner)
        return inventory

    def _build_agent_config_fingerprint(self) -> str:
        payload = self.config_options()
        payload["uid"] = self.uid
        return stable_fingerprint(payload)

    def _build_agent_definition_fingerprint(self, inventory: dict[str, dict] = None) -> str:
        if inventory is None:
            inventory = self._build_element_inventory()
        payload = {
            "id": self.id,
            "uid": self.uid,
            "type": self.__class__.__name__,
            "elements": {uid: record["definition_fingerprint"] for uid, record in sorted(inventory.items())},
        }
        return stable_fingerprint(payload)

    def _persist_checkpoint_status(self, success: bool, reason: str, error: str = None):
        self._last_checkpoint_success = success
        self._last_checkpoint_reason = reason
        self._last_checkpoint_error = error
        self._last_checkpoint_timestamp = TimeUtils.utc_ms()
        self._runtime_storage.set_runtime_value("last_checkpoint_success", success)
        self._runtime_storage.set_runtime_value("last_checkpoint_reason", reason)
        self._runtime_storage.set_runtime_value("last_checkpoint_error", error)
        self._runtime_storage.set_runtime_value("last_checkpoint_timestamp", self._last_checkpoint_timestamp)

    def _persist_reconciliation_report(self, report: dict):
        self._last_reconciliation_report = report
        self._runtime_storage.set_runtime_value("last_reconciliation_report", report)

    def _start_auto_checkpoint_thread(self):
        self._sync_auto_checkpoint_config()
        if not self._auto_checkpoint_config.enabled or self._auto_checkpoint_config.interval_seconds <= 0:
            return
        self._checkpoint_stop_event.clear()
        if self._checkpoint_thread is not None and self._checkpoint_thread.is_alive():
            return
        self._checkpoint_thread = threading.Thread(target=self._auto_checkpoint_loop, name=f"CheckpointThread-{self.id}", daemon=True)
        self._checkpoint_thread.start()

    def _stop_auto_checkpoint_thread(self):
        self._checkpoint_stop_event.set()
        if self._checkpoint_thread is not None and self._checkpoint_thread.is_alive():
            self._checkpoint_thread.join(timeout=2.0)
        self._checkpoint_thread = None

    def _auto_checkpoint_loop(self):
        while not self._checkpoint_stop_event.wait(timeout=0.25):
            if not self._is_running:
                continue
            if self._lifecycle_state in {
                AgentLifecycleState.CHECKPOINTING,
                AgentLifecycleState.RESTORING,
                AgentLifecycleState.STOPPING,
            }:
                continue
            if self._last_checkpoint_timestamp is not None:
                elapsed = (TimeUtils.utc_ms() - self._last_checkpoint_timestamp) / 1000.0
                if elapsed < max(self._auto_checkpoint_config.interval_seconds, self._auto_checkpoint_config.min_seconds_between_checkpoints):
                    continue
            try:
                self.checkpoint(checkpoint_reason=CheckpointReason.AUTO_TIMER.value)
            except Exception as e:
                logger.error(f"Automatic checkpoint failed for Agent(id='{self.id}'): {e}")

    def _inventory_records_match(self, current_record: dict | None, saved_record: dict | None) -> bool:
        if current_record is None or saved_record is None:
            return False
        return (
            current_record.get("uid") == saved_record.get("uid")
            and current_record.get("type") == saved_record.get("type")
            and current_record.get("definition_fingerprint") == saved_record.get("definition_fingerprint")
        )

    def _auto_resume_from_current_checkpoint(self) -> dict:
        if self.resume_mode == ResumeMode.DISABLED.value:
            report = ReconciliationReport(
                resume_mode=self.resume_mode,
                checkpoint_id=None,
                created_at=TimeUtils.utc_ms(),
            ).to_dict()
            self._persist_reconciliation_report(report)
            return report
        checkpoint_id = self._runtime_storage.get_current_checkpoint()
        if checkpoint_id is None:
            report = ReconciliationReport(
                resume_mode=self.resume_mode,
                checkpoint_id=None,
                created_at=TimeUtils.utc_ms(),
            ).to_dict()
            self._persist_reconciliation_report(report)
            return report
        manifest = self._runtime_storage.load_manifest(checkpoint_id)
        if manifest is None:
            report = ReconciliationReport(
                resume_mode=self.resume_mode,
                checkpoint_id=checkpoint_id,
                created_at=TimeUtils.utc_ms(),
            ).to_dict()
            self._persist_reconciliation_report(report)
            return report
        current_inventory = self._build_element_inventory()
        saved_inventory = manifest.get("element_inventory", {})
        report = ReconciliationReport(
            resume_mode=self.resume_mode,
            checkpoint_id=checkpoint_id,
            created_at=TimeUtils.utc_ms(),
        )
        current_elements = {element.uid: element for element in self.get_all_elements()}
        self._set_lifecycle_state(AgentLifecycleState.RESTORING)
        for uid, element in current_elements.items():
            current_record = current_inventory.get(uid)
            saved_record = saved_inventory.get(uid)
            if self._inventory_records_match(current_record, saved_record):
                snapshot = self._runtime_storage.load_element_snapshot(checkpoint_id, uid)
                if snapshot is not None and element.restore(snapshot=snapshot, agent=self):
                    report.restored.append(
                        ElementReconciliationResult(
                            uid=uid,
                            id=element.id,
                            type=element.type,
                            outcome=ElementReconciliationOutcome.RESTORE_EXACT_MATCH.value,
                            reason="exact-match",
                        )
                    )
                    continue
            report.fresh_started.append(
                ElementReconciliationResult(
                    uid=uid,
                    id=element.id,
                    type=element.type,
                    outcome=ElementReconciliationOutcome.FRESH_START_CHANGED.value,
                    reason="changed-or-missing",
                )
            )
        for uid, saved_record in saved_inventory.items():
            if uid not in current_elements:
                report.removed_ignored.append(
                    ElementReconciliationResult(
                        uid=uid,
                        id=saved_record.get("id"),
                        type=saved_record.get("type"),
                        outcome=ElementReconciliationOutcome.REMOVED_IGNORED.value,
                        reason="missing-in-current-agent",
                    )
                )
        report.exact_match = (
            len(report.fresh_started) == 0
            and len(report.removed_ignored) == 0
            and len(report.restored) == len(current_elements)
        )
        report_dict = report.to_dict()
        self._persist_reconciliation_report(report_dict)
        self._set_lifecycle_state(AgentLifecycleState.READY)
        return report_dict
           
    def _disconnect_adapters(self):
        """ Disconnect all `Adapter`s in the `Agent`.
        
        Logs errors for adapters that fail to disconnect.
        """
        for adapter in self.adapter_store.values():
            if adapter.disconnect() is False:
                logger.error(adapter.name() + " could not be disconnected")
        
    def _stop_services(self):
        """ Stop all `Service`s in the `Agent`.
        """
        for service in self.service_store.values():
            service.stop()

    def _pause_services(self):
        for service in self.service_store.values():
            if hasattr(service, "pause"):
                service.pause()

    def _resume_services(self):
        for service in self.service_store.values():
            if hasattr(service, "resume"):
                service.resume()

    def _quiesce_services(self):
        for service in self.service_store.values():
            if hasattr(service, "quiesce"):
                service.quiesce()
                   
    def _connect_adapters(self):
        """ Connect all `Adapter`s in the `Agent`.        
        """
        for adapter in self.adapter_store.values():
            if adapter.connect() is False:
                logger.error(adapter.name() + " could not be connected")           
                
    def _start_services(self):
        """ Start all `Service`s in the `Agent`
        """
        for service in self.service_store.values():
            if service.auto_start:
                service.start()
    
    def release(self, blocking : bool = True):
        """Release the `Agent` for operation.
        
        Installs all elements, connects adapters, and starts services. If blocking is True,
        waits until the stop event is set (typically by calling terminate()).
        
        Args:
            blocking (bool, optional): Whether to block until Agent is terminated. Defaults to True.
        """
        with self._control_lock:
            self._finalize_runtime_identities()
            self._sync_auto_checkpoint_config()
            self._runtime_storage.ensure_layout()
            self.save_config()
            self._set_lifecycle_state(AgentLifecycleState.CREATED)
            self._install_elements()
            self._auto_resume_from_current_checkpoint()
            self._connect_adapters()
            self._start_services()
            self._stop_event.clear()
            self._is_running = True
            self._run_id = self._runtime_storage.start_run()
            self._start_auto_checkpoint_thread()
            self._set_lifecycle_state(AgentLifecycleState.RUNNING)
            logger.info(f"Started {self.__class__.__name__} application (id='{self.id}')")
        if blocking:
            self._stop_event.wait()  # blocks efficiently until the event is set (for example by terminate)
                
    def terminate(self):
        """ Terminate the `Agent`.
        
        Stops all services, disconnects adapters, and uninstalls elements.
        Signals the stop event to unblock any waiting release() call.
        """
        with self._control_lock:
            if self.auto_checkpoint_on_terminate and self._is_running:
                try:
                    self.checkpoint(
                        checkpoint_reason=CheckpointReason.TERMINATE.value,
                        resume_after=False,
                    )
                except Exception as e:
                    logger.error(f"Terminate checkpoint failed for Agent(id='{self.id}'): {e}")
            self._stop_auto_checkpoint_thread()
            self._set_lifecycle_state(AgentLifecycleState.STOPPING)
            self._stop_services()
            self._disconnect_adapters()
            self._uninstall_elements()
            self._is_running = False
            self._runtime_storage.stop_run(self._run_id)
            self._run_id = None
            self._stop_event.set()
            self._set_lifecycle_state(AgentLifecycleState.STOPPED)

    def pause(self):
        with self._control_lock:
            if not self._is_running:
                return
            self._set_lifecycle_state(AgentLifecycleState.PAUSING)
            self._pause_services()
            self._set_lifecycle_state(AgentLifecycleState.PAUSED)

    def resume(self):
        with self._control_lock:
            if not self._is_running:
                return
            self._resume_services()
            self._set_lifecycle_state(AgentLifecycleState.RUNNING)

    def quiesce(self, checkpoint_if_configured: bool = True):
        with self._control_lock:
            if not self._is_running:
                return
            self._set_lifecycle_state(AgentLifecycleState.QUIESCING)
            self._quiesce_services()
            if checkpoint_if_configured and self.auto_checkpoint_on_quiesce:
                self.checkpoint(
                    checkpoint_reason=CheckpointReason.QUIESCE.value,
                    resume_after=False,
                    quiesce_first=False,
                )

    def checkpoint(
        self,
        checkpoint_id: str = None,
        checkpoint_reason: str = CheckpointReason.MANUAL.value,
        resume_after: bool | None = None,
        quiesce_first: bool = True,
    ) -> dict:
        with self._control_lock:
            with self._checkpoint_lock:
                self._finalize_runtime_identities()
                self._sync_auto_checkpoint_config()
                self._runtime_storage.ensure_layout()
                self.save_config()
                checkpoint_id = checkpoint_id or self._runtime_storage.create_checkpoint_id()
                prior_state = self._lifecycle_state
                should_resume = resume_after if resume_after is not None else (self._is_running and prior_state == AgentLifecycleState.RUNNING)
                if self._is_running and quiesce_first:
                    self.quiesce(checkpoint_if_configured=False)
                self._set_lifecycle_state(AgentLifecycleState.CHECKPOINTING)
                self._runtime_storage.create_checkpoint_dir(checkpoint_id)
                inventory = self._build_element_inventory()
                element_files : dict[str, str] = {}
                try:
                    for element in self.get_all_elements():
                        snapshot = element.checkpoint(agent=self)
                        if snapshot.metadata is None:
                            snapshot.metadata = {}
                        snapshot.metadata["inventory_record"] = inventory.get(element.uid, {})
                        path = self._runtime_storage.write_element_snapshot(checkpoint_id, snapshot)
                        element_files[element.uid] = str(path)
                    manifest = CheckpointManifest(
                        checkpoint_id=checkpoint_id,
                        agent_uid=self.uid,
                        agent_id=self.id,
                        created_at=TimeUtils.utc_ms(),
                        lifecycle_state=prior_state.value,
                        run_id=self._run_id,
                        checkpoint_reason=checkpoint_reason,
                        agent_type=self.__class__.__name__,
                        agent_config_fingerprint=self._build_agent_config_fingerprint(),
                        agent_definition_fingerprint=self._build_agent_definition_fingerprint(inventory),
                        element_files=element_files,
                        element_inventory=inventory,
                        metadata={
                            "service_ids": list(self.service_store.keys()),
                            "buffer_ids": list(self.buffer_store.keys()),
                            "adapter_ids": list(self.adapter_store.keys()),
                        },
                    )
                    self._runtime_storage.write_manifest(manifest)
                    self._persist_checkpoint_status(True, checkpoint_reason)
                except Exception as e:
                    self._persist_checkpoint_status(False, checkpoint_reason, str(e))
                    self._set_lifecycle_state(prior_state)
                    raise
                if should_resume:
                    self.resume()
                else:
                    self._set_lifecycle_state(prior_state)
                return manifest.to_dict()

    def restore(self, checkpoint_id: str = None) -> bool:
        with self._control_lock:
            self._finalize_runtime_identities()
            checkpoint_id = checkpoint_id or self._runtime_storage.get_current_checkpoint()
            if checkpoint_id is None:
                return False
            manifest = self._runtime_storage.load_manifest(checkpoint_id)
            if manifest is None:
                return False
            prior_state = self._lifecycle_state
            should_resume = self._is_running and prior_state == AgentLifecycleState.RUNNING
            if self._is_running:
                self.quiesce(checkpoint_if_configured=False)
            self._set_lifecycle_state(AgentLifecycleState.RESTORING)
            for element in self.get_all_elements():
                snapshot = self._runtime_storage.load_element_snapshot(checkpoint_id, element.uid)
                if snapshot is not None:
                    element.restore(snapshot=snapshot, agent=self)
            if should_resume:
                self.resume()
            else:
                restored_state = manifest.get("lifecycle_state", prior_state.value if hasattr(prior_state, "value") else str(prior_state))
                self._set_lifecycle_state(AgentLifecycleState(restored_state))
            return True

    def reload_current(self) -> bool:
        manifest = self.checkpoint(
            checkpoint_reason=CheckpointReason.RELOAD.value,
            resume_after=False,
        )
        checkpoint_id = manifest["checkpoint_id"]
        return self.restore(checkpoint_id=checkpoint_id)

    def save_config(self, file_path: str | Path = None) -> Path:
        self._finalize_runtime_identities()
        payload = self.config_options()
        payload["uid"] = self.uid
        target = Path(file_path) if file_path is not None else self._runtime_storage.config_root / "agent.json"
        FileUtils.create_dir(str(target.parent))
        with open(target, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=4)
        return target

    def load_config(self, file_path: str | Path = None) -> bool:
        target = Path(file_path) if file_path is not None else self._runtime_storage.config_root / "agent.json"
        if not target.exists():
            return False
        with open(target, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        for property_name, value in payload.items():
            if isinstance(value, dict) and len(value) == 0:
                setattr(self, property_name, {})
            elif isinstance(value, list) and len(value) == 0:
                setattr(self, property_name, [])
            else:
                ClassUtils.set_property(self, property_name, value)
        if "uid" in payload:
            self._uid_explicit = True
        self._ensure_runtime_storage_matches_uid()
        self._sync_auto_checkpoint_config()
        return True

    def cleanup(self, scope: str = CleanupScope.REBUILDABLE_OWNER_CACHE.value, dry_run: bool = False, keep_last_n_checkpoints: int = 3) -> dict:
        deleted : list[str] = []
        skipped : list[str] = []
        candidates : list[str] = []
        for element in self.get_all_elements():
            report : CleanupReport = element.cleanup(scope=scope, dry_run=dry_run)
            deleted.extend(report.deleted)
            skipped.extend(report.skipped)
            candidates.extend(report.candidates)
        if scope == CleanupScope.TMP_ONLY.value:
            for path in self._runtime_storage.runtime_tmp_paths():
                candidates.append(str(path))
                if dry_run:
                    continue
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)
                deleted.append(str(path))
        if scope == CleanupScope.CHECKPOINT_RETENTION_PRUNING.value:
            checkpoints = self._runtime_storage.list_checkpoints()
            current_checkpoint = self._runtime_storage.get_current_checkpoint()
            for checkpoint_id in checkpoints[keep_last_n_checkpoints:]:
                if checkpoint_id == current_checkpoint:
                    skipped.append(checkpoint_id)
                    continue
                checkpoint_dir = self._runtime_storage.checkpoints_root / checkpoint_id
                candidates.append(str(checkpoint_dir))
                if dry_run:
                    continue
                import shutil
                shutil.rmtree(checkpoint_dir, ignore_errors=True)
                deleted.append(str(checkpoint_dir))
        return {
            "scope": scope,
            "dry_run": dry_run,
            "deleted": deleted,
            "skipped": skipped,
            "candidates": candidates,
        }

    def status(self) -> dict:
        return {
            "id": self.id,
            "uid": self.uid,
            "description": self.description,
            "is_running": self._is_running,
            "lifecycle_state": self._lifecycle_state.value,
            "run_id": self._run_id,
            "current_checkpoint_id": self._runtime_storage.get_current_checkpoint(),
            "resume_mode": self.resume_mode,
            "auto_checkpoint_config": self._auto_checkpoint_config.to_dict(),
            "last_checkpoint_reason": self._last_checkpoint_reason,
            "last_checkpoint_success": self._last_checkpoint_success,
            "last_checkpoint_error": self._last_checkpoint_error,
            "last_checkpoint_timestamp": self._last_checkpoint_timestamp,
            "last_reconciliation_report": self._last_reconciliation_report,
            "buffers": {buffer.id: str(buffer.get_state().value if hasattr(buffer.get_state(), "value") else buffer.get_state()) for buffer in self.buffer_store.values()},
            "adapters": {adapter.id: str(adapter.get_state().value if hasattr(adapter.get_state(), "value") else adapter.get_state()) for adapter in self.adapter_store.values()},
            "services": {service.id: str(service.get_state().value if hasattr(service.get_state(), "value") else service.get_state()) for service in self.service_store.values()},
        }
            
    def get_adapter(self, id : str) -> Adapter:
        """ return the `Adapter` specified by `id`
        Args:
            id (str): _description_

        Returns:
            Adapter: _description_
        """
        if id in self.adapter_store:
            return self.adapter_store[id]    
        else:
            logger.error("No Adapter with id=" + id + " was found")
            return None
        
    def get_buffer(self, id : str) -> Buffer:
        """ return the `Buffer` specified by `id`

        Args:
            id (str): unique id of the `Buffer`

        Returns:
            Buffer: `Buffer` instance
        """
        if id in self.buffer_store:
            return self.buffer_store[id]    
        else:
            logger.error(f"No Buffer with id={id} was found")
            return None
        
    def get_service(self, id : str) -> Service:
        """ return the `Service` specified by `id`
        """
        if id in self.service_store:
            return self.service_store[id]    
        else:
            logger.error("No Service with id=" + id + " was found")
            return None
        
    def get_services(self, type : Type) -> list[Service]:
        """returns all services of a specified type/class

        Args:
            type (Type): class

        Returns:
            list[Service]: list of services with the specified type
        """
        services = list()
        for service in self.service_store.values():
            if isinstance(service, type):
                services.append(service)
        return services
           
    def get_element(self, id : str) -> AgentElement:
        """Return the `AgentElement` with the specified `id`.
        """        
        if id in self.adapter_store:
            return self.adapter_store[id]
        elif id in self.buffer_store:
            return self.buffer_store[id]
        elif id in self.service_store:
            return self.service_store[id]
        else:
            return self._get_deep_element(id)
            
    def get_node(self, id : str, service_id : str = None) -> Node:
        """Return the `Node` with the specified `id`.

        If `service_id` is given, the search is limited to that `Service` (expected to be a
        `StatemachineService`). Otherwise, all services are searched for a node with the
        matching id.

        Args:
            id (str): Unique id of the `Node` to retrieve.
            service_id (str, optional): Unique id of the `Service` to restrict the search to.
                Defaults to None.

        Returns:
            Node: The `Node` instance if found, otherwise `None`.
        """
        if service_id:
            service = self.get_service(service_id)
            if service:
                if isinstance(service, StatemachineService):
                    if id in service.nodes:
                        return service.nodes[id]
                    else:
                        logger.error(f"specified {Node.cname()} with id={id} was not found in  with id={service_id}")                        
                else:
                    logger.error(f"specified Service is not of type {StatemachineService.cname()}")     
                    return None
            else:
                logger.error(f"no Service with id={service_id} was found!")
                return None
        else:
            node : Node = None
            for service in self.service_store.values():            
                if isinstance(service, StatemachineService):
                    if id in service.nodes:
                        node =  service.nodes[id]
            if node:
                return node
            else:
                logger.error(f"no {Node.cname()} with id={id} was found!")
                return None
    
    def _get_deep_element(self, id : str) -> AgentElement:
        """checks for nested `AgentElement`s

        Args:
            id (str): unique id

        Returns:
            AgentElement:
        """
        for adapter in self.adapter_store.values():
            for attr_name, attr_value in vars(adapter).items():
                #print(f"{attr_name}: {type(attr_value)}")
                if isinstance(attr_value, AgentElement):
                    if attr_value.id == id:
                        return attr_value
            for buffer in self.buffer_store.values():
                for attr_name, attr_value in vars(buffer).items():
                    #print(f"{attr_name}: {type(attr_value)}")
                    if isinstance(attr_value, AgentElement):
                        if attr_value.id == id:
                            return attr_value
        for service in self.service_store.values():
            for attr_name, attr_value in vars(service).items():
                #print(f"{attr_name}: {type(attr_value)}")
                if isinstance(attr_value, AgentElement):
                    if attr_value.id == id:
                        return attr_value
            # special case for statemachine services, look into nodes
            if isinstance(service, StatemachineService):
                for node in service.nodes.values():
                    if cast(Node, node).id == id:
                        return node
        return None

    def get_all_elements(self) -> list[AgentElement]:
        elements : list[AgentElement] = []
        elements.extend(self.adapter_store.values())
        elements.extend(self.buffer_store.values())
        elements.extend(self.service_store.values())
        for service in self.service_store.values():
            if isinstance(service, StatemachineService):
                elements.extend(service.nodes.values())
        return elements
    
    def is_running(self) -> bool:
        """Check if the Agent is currently running.
        
        Returns:
            bool: True if the Agent is running, False otherwise.
        """
        return self._is_running

    def get_lifecycle_state(self) -> AgentLifecycleState:
        return self._lifecycle_state

    def _set_lifecycle_state(self, state: AgentLifecycleState):
        self._lifecycle_state = state
        self._runtime_storage.set_lifecycle_state(state.value)
     
