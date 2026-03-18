from __future__ import annotations
import copy
import json
import shutil
from typing import TYPE_CHECKING, Any
from abc import ABC, abstractmethod
from dataclasses import MISSING, dataclass, field, fields
from enum import Enum
from pathlib import Path
import uuid
from loguru import logger


from .AgentStates import AgentElementState
from .RuntimeStorage import (
    ArtifactPolicy,
    ArtifactRecord,
    CleanupReport,
    CleanupScope,
    ElementSnapshot,
    RuntimeStorage,
    normalize_runtime_key,
    stable_fingerprint,
)
from ..utils.ClassUtils import ClassUtils
from ..utils.FileUtils import FileUtils

if TYPE_CHECKING:
    from .Agent import Agent


PERSISTENCE_ROLE_KEY = "pydag_persistence_role"
ARTIFACT_KIND_KEY = "pydag_artifact_kind"
ARTIFACT_POLICY_KEY = "pydag_artifact_policy"
ARTIFACT_MANAGED_KEY = "pydag_artifact_managed"
ARTIFACT_NAME_KEY = "pydag_artifact_name"


class PersistenceRole(str, Enum):
    PERSISTED = "persisted"
    ARTIFACT = "artifact"
    TRANSIENT = "transient"
    RUNTIME_HANDLE = "runtime_handle"


def _persistence_field(
    role: str,
    *,
    default=MISSING,
    default_factory=MISSING,
    metadata: dict | None = None,
    **kwargs,
):
    merged = dict(metadata or {})
    merged["config"] = False
    merged[PERSISTENCE_ROLE_KEY] = role
    field_kwargs = {"compare": False}
    field_kwargs.update(kwargs)
    if default is not MISSING:
        field_kwargs["default"] = default
    if default_factory is not MISSING:
        field_kwargs["default_factory"] = default_factory
    field_kwargs["metadata"] = merged
    return field(**field_kwargs)


def persisted_field(*, default=MISSING, default_factory=MISSING, metadata: dict | None = None, **kwargs):
    return _persistence_field(
        PersistenceRole.PERSISTED.value,
        default=default,
        default_factory=default_factory,
        metadata=metadata,
        **kwargs,
    )


def artifact_descriptor_field(
    *,
    default=MISSING,
    default_factory=MISSING,
    name: str | None = None,
    kind: str = "artifact",
    policy: str = ArtifactPolicy.DURABLE.value,
    managed: bool = True,
    metadata: dict | None = None,
    **kwargs,
):
    merged = dict(metadata or {})
    merged[ARTIFACT_KIND_KEY] = kind
    merged[ARTIFACT_POLICY_KEY] = policy
    merged[ARTIFACT_MANAGED_KEY] = managed
    if name is not None:
        merged[ARTIFACT_NAME_KEY] = name
    return _persistence_field(
        PersistenceRole.ARTIFACT.value,
        default=default,
        default_factory=default_factory,
        metadata=merged,
        **kwargs,
    )


def transient_field(*, default=MISSING, default_factory=MISSING, metadata: dict | None = None, **kwargs):
    return _persistence_field(
        PersistenceRole.TRANSIENT.value,
        default=default,
        default_factory=default_factory,
        metadata=metadata,
        **kwargs,
    )


def runtime_handle_field(*, default=MISSING, default_factory=MISSING, metadata: dict | None = None, **kwargs):
    return _persistence_field(
        PersistenceRole.RUNTIME_HANDLE.value,
        default=default,
        default_factory=default_factory,
        metadata=metadata,
        **kwargs,
    )


@dataclass
class AgentElement(ABC):
    """
    Abstract base class for agent elements.
    """

    type : str = field(default=None, metadata={"description": "fully qualified package and class name descriptor"})
    id : str = field(default=None, metadata = {"description": "unique identifier of element in DataGrabber application"})
    load_on_install : bool = field(default=False, metadata = {"description": "specifies whether the GrabberElement should try to load from local json config file on install"})
    uid : str = field(default=None)
    _uid_explicit : bool = transient_field(default=False, init=False, repr=False)
    _owner_scope : str | None = transient_field(default=None, init=False, repr=False)
    _state : AgentElementState = transient_field(default=AgentElementState.UNINSTALLED, init=False, repr=False)
    _managed_artifacts : list[ArtifactRecord] = transient_field(default_factory=list, init=False, repr=False)
      
    def __post_init__(self):
        """
        Initialize the agent element and assign a unique ID.
        """
        self.type = self.__module__                   
        if self.id is None: 
            self.id = self.unique_id()
        self._uid_explicit = self.uid is not None
        if self.uid is None:
            self.uid = self._build_auto_uid()
        self._state = AgentElementState.UNINSTALLED
        self._validate_persistence_schema()
        
    def name(self) -> str:
        s = self.__class__.__name__ + "[" + self.id + "]"
        return s
    
    @classmethod
    def cname(cls) -> str:
        s = cls.__name__
        return s

    def config_options(self, with_descriptions = False) -> dict:
        from .AgentConfig import AgentConfig
        result = AgentConfig.config_options(self, with_descriptions)
        return result

    @classmethod
    def unique_id(cls):
        """
        Generate a unique ID for the agent element class
        
        Returns:
            str: A unique identifier for the agent element class
        """
        return f"{cls.__name__} [{uuid.uuid4()}]"
    
    @abstractmethod
    def _on_install(self, agent : Agent = None):
        """ installation logic for the element, can be used to reference other agent elements

        Args:
            agent (Agent, optional): _description_. Defaults to None.
        """
    
    @abstractmethod
    def _on_uninstall(self, agent : Agent = None):
        """ uninstallation logic for the element

        Args:
            agent (Agent, optional): _description_. Defaults to None.
        """
    
    def install(self, agent : Agent = None):
        """initializes the element with respect to startup functionality or initial internal object creation,
           if agent is not None, it can be used to reference or create other agent elements
           the method should always be used in child classes with super().install()
        """
        if self.load_on_install:
            self.load_config(agent=agent)
        self._on_install(agent)
        self._state = AgentElementState.INSTALLED
        
    def uninstall(self, agent : Agent = None):
        """resets the element, this method can be used to stop internal element logic or reset objects that were initialized on creation
        """
        self._on_uninstall(agent)
        self._state = AgentElementState.UNINSTALLED
        return
    
    def load(self):
        self.load_config()
    
    def save(self):
        self.save_config()
            
    def get_state(self) -> AgentElementState:
        """
        method to get the current state of the element
        Returns:
            AgentState: current state of the element
        """
        return self._state
    
    def set_state(self, state : AgentElementState):
        """ method to set the `AgentElement`s internal `state`

        Args:
            state (AgentElementState): state enum
        """
        self._state = state

    def save_config(self, file_path: str | Path = None, agent: Agent = None) -> Path:
        target = Path(file_path) if file_path is not None else self._default_config_path(agent)
        payload = self.config_options()
        payload["uid"] = self.uid
        FileUtils.create_dir(str(target.parent))
        with open(target, "w", encoding="utf-8") as json_file:
            json.dump(payload, json_file, indent=4)
        return target

    def load_config(self, file_path: str | Path = None, agent: Agent = None) -> bool:
        target = Path(file_path) if file_path is not None else self._default_config_path(agent)
        if target.exists():
            with open(target, "r", encoding="utf-8") as json_file:
                d = json.load(json_file)
                ClassUtils.set_properties(self, d)
                if "uid" in d:
                    self._uid_explicit = True
            return True
        logger.warning("no configuration file " + str(target) + " to load from was found")
        return False

    def snapshot_state(self) -> dict:
        payload : dict[str, Any] = {}
        for field_info in self._iter_persistence_fields(PersistenceRole.PERSISTED.value):
            value = getattr(self, field_info.name)
            payload[field_info.name] = self._snapshot_copy(value)
        return payload

    def restore_state(self, payload: dict | None):
        if payload is None:
            return
        for field_info in self._iter_persistence_fields(PersistenceRole.PERSISTED.value):
            if field_info.name in payload:
                setattr(self, field_info.name, self._snapshot_copy(payload[field_info.name]))
        return

    def list_owned_artifacts(self) -> list[ArtifactRecord]:
        return self._dedupe_artifacts(
            self._collect_declared_artifacts() + list(self._managed_artifacts) + list(self.describe_additional_artifacts())
        )

    def get_config_fingerprint(self, agent: Agent = None) -> str:
        return stable_fingerprint(self.config_options())

    def get_owner_scope(self, agent: Agent = None) -> str | None:
        return self._owner_scope

    def get_topology_fingerprint(self, agent: Agent = None) -> str | None:
        return None

    def get_persistence_schema(self) -> dict[str, dict[str, Any]]:
        schema : dict[str, dict[str, Any]] = {}
        for field_info in fields(self):
            role = field_info.metadata.get(PERSISTENCE_ROLE_KEY)
            if role is None:
                continue
            entry : dict[str, Any] = {"role": role}
            if role == PersistenceRole.ARTIFACT.value:
                entry.update(
                    {
                        "kind": field_info.metadata.get(ARTIFACT_KIND_KEY, "artifact"),
                        "policy": field_info.metadata.get(ARTIFACT_POLICY_KEY, ArtifactPolicy.DURABLE.value),
                        "managed": field_info.metadata.get(ARTIFACT_MANAGED_KEY, True),
                        "name": field_info.metadata.get(ARTIFACT_NAME_KEY, field_info.name.lstrip("_")),
                    }
                )
            schema[field_info.name] = entry
        return schema

    def get_persistence_schema_fingerprint(self) -> str:
        return stable_fingerprint(self.get_persistence_schema())

    def get_definition_fingerprint(self, agent: Agent = None) -> str:
        payload = {
            "uid": self.uid,
            "id": self.id,
            "type": self.type,
            "config_fingerprint": self.get_config_fingerprint(agent),
            "persistence_schema_fingerprint": self.get_persistence_schema_fingerprint(),
            "owner_scope": self.get_owner_scope(agent),
            "topology_fingerprint": self.get_topology_fingerprint(agent),
        }
        return stable_fingerprint(payload)

    def prepare_checkpoint(self, agent: Agent = None):
        return

    def save_owned_artifacts(self, checkpoint_id: str | None = None, agent: Agent = None):
        return

    def load_owned_artifacts(self, snapshot: dict | None = None, agent: Agent = None):
        return

    def describe_additional_artifacts(self) -> list[ArtifactRecord]:
        return []

    def rebuild_runtime_handles(self, agent: Agent = None):
        return

    def validate_restored_state(self, snapshot: dict | None = None) -> bool:
        return True

    def register_artifact(
        self,
        name: str,
        path: str | Path,
        kind: str = "artifact",
        policy: str = ArtifactPolicy.DURABLE.value,
        managed: bool = True,
        metadata: dict | None = None,
    ) -> ArtifactRecord:
        record = ArtifactRecord(
            name=name,
            path=str(Path(path)),
            kind=kind,
            policy=policy,
            managed=managed,
            metadata={} if metadata is None else metadata,
        )
        self._managed_artifacts.append(record)
        return record

    def clear_registered_artifacts(self):
        self._managed_artifacts = []

    def build_snapshot(self, agent: Agent = None) -> ElementSnapshot:
        self.prepare_checkpoint(agent=agent)
        self.save_owned_artifacts(agent=agent)
        artifacts = self.list_owned_artifacts()
        state_value = self._state.value if hasattr(self._state, "value") else str(self._state)
        return ElementSnapshot(
            uid=self.uid,
            id=self.id,
            type=self.type,
            state=state_value,
            config_fingerprint=self.get_config_fingerprint(agent),
            definition_fingerprint=self.get_definition_fingerprint(agent),
            persistence_schema_fingerprint=self.get_persistence_schema_fingerprint(),
            topology_fingerprint=self.get_topology_fingerprint(agent),
            payload=self.snapshot_state(),
            artifacts=artifacts,
            metadata={
                "owner_scope": self.get_owner_scope(agent),
                "config_payload": self.config_options(),
                "class_name": self.__class__.__name__,
                "persistence_schema": self.get_persistence_schema(),
            },
        )

    def restore_from_snapshot(self, snapshot: dict | None, agent: Agent = None) -> bool:
        if snapshot is None:
            return False
        self.restore_state(snapshot.get("payload", {}))
        self._restore_declared_artifact_fields(snapshot.get("artifacts", []))
        self.load_owned_artifacts(snapshot=snapshot, agent=agent)
        self.rebuild_runtime_handles(agent=agent)
        if not self.validate_restored_state(snapshot):
            return False
        state = snapshot.get("state")
        if state is not None:
            self._restore_state_enum(state)
        return True

    def list_cleanup_targets(self) -> list[ArtifactRecord]:
        return self.list_owned_artifacts()

    def cleanup(self, scope: str = CleanupScope.REBUILDABLE_OWNER_CACHE.value, dry_run: bool = False) -> CleanupReport:
        report = CleanupReport(scope=scope, dry_run=dry_run)
        for artifact in self.list_cleanup_targets():
            if not self._artifact_matches_scope(artifact, scope):
                report.skipped.append(artifact.path)
                continue
            path = Path(artifact.path)
            if not path.exists():
                report.skipped.append(artifact.path)
                continue
            report.candidates.append(str(path))
            if dry_run:
                continue
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
            report.deleted.append(str(path))
        return report

    def cleanup_dry_run(self, scope: str = CleanupScope.REBUILDABLE_OWNER_CACHE.value) -> CleanupReport:
        return self.cleanup(scope=scope, dry_run=True)

    def checkpoint(self, agent: Agent = None) -> ElementSnapshot:
        return self.build_snapshot(agent=agent)

    def restore(self, snapshot: dict | None, agent: Agent = None) -> bool:
        return self.restore_from_snapshot(snapshot=snapshot, agent=agent)

    def get_runtime_storage(self, agent: Agent = None) -> RuntimeStorage:
        owner_uid = self._runtime_owner_uid(agent)
        storage = RuntimeStorage(owner_uid)
        storage.ensure_layout()
        return storage

    def get_runtime_root(self, agent: Agent = None) -> Path:
        return self.get_runtime_storage(agent).runtime_root

    def get_state_root(self, agent: Agent = None) -> Path:
        return self.get_artifact_root(agent) / "state"

    def get_runtime_artifacts_root(self, agent: Agent = None) -> Path:
        storage = self.get_runtime_storage(agent)
        root = storage.artifacts_root
        FileUtils.create_dir(str(root))
        return root

    def get_runtime_artifact_subdir(self, *parts: str | Path, agent: Agent = None) -> Path:
        root = self.get_runtime_artifacts_root(agent).joinpath(*parts)
        FileUtils.create_dir(str(root))
        return root

    def get_artifact_root(self, agent: Agent = None) -> Path:
        storage = self.get_runtime_storage(agent)
        root = storage.artifacts_root / self.__class__.__name__ / self.uid
        FileUtils.create_dir(str(root))
        return root

    def get_owned_artifact_subdir(self, *parts: str | Path, agent: Agent = None) -> Path:
        root = self.get_artifact_root(agent).joinpath(*parts)
        FileUtils.create_dir(str(root))
        return root

    def _runtime_owner_uid(self, agent: Agent = None) -> str:
        if agent is not None and hasattr(agent, "uid"):
            return agent.uid
        agent_ref = getattr(self, "_agent", None)
        if agent_ref is not None and hasattr(agent_ref, "uid"):
            return agent_ref.uid
        return self.uid

    def refresh_runtime_identity(self, uid_prefix: str = None, owner_scope: str = None):
        if owner_scope is not None:
            self._owner_scope = owner_scope
        if not self._uid_explicit:
            prefix = uid_prefix or self._default_uid_prefix()
            slug = normalize_runtime_key(self.id, fallback=normalize_runtime_key(self.__class__.__name__))
            parts = [self._owner_scope, prefix, slug]
            self.uid = "/".join([part for part in parts if part])
        return self.uid

    def _default_config_path(self, agent: Agent = None) -> Path:
        storage = self.get_runtime_storage(agent)
        target = storage.config_root / "elements" / f"{self.uid}.json"
        FileUtils.create_dir(str(target.parent))
        return target

    def _default_uid_prefix(self) -> str:
        return normalize_runtime_key(self.__class__.__name__)

    def _build_auto_uid(self) -> str:
        prefix = self._default_uid_prefix()
        slug = normalize_runtime_key(self.id, fallback=normalize_runtime_key(self.__class__.__name__))
        return "/".join([prefix, slug])

    def _restore_state_enum(self, state_value: str):
        try:
            self._state = type(self._state)(state_value)
        except Exception:
            try:
                self._state = AgentElementState(state_value)
            except Exception:
                logger.debug(f"Could not restore state '{state_value}' for {self.name()}")

    def _artifact_matches_scope(self, artifact: ArtifactRecord, scope: str) -> bool:
        if scope == CleanupScope.TMP_ONLY.value:
            return artifact.policy == ArtifactPolicy.EPHEMERAL.value
        if scope == CleanupScope.REBUILDABLE_OWNER_CACHE.value:
            return artifact.policy in {
                ArtifactPolicy.EPHEMERAL.value,
                ArtifactPolicy.REBUILDABLE.value,
            }
        if scope == CleanupScope.SHARED_CACHE_PRUNE.value:
            return artifact.policy == ArtifactPolicy.SHARED.value
        return False

    def _iter_persistence_fields(self, role: str | None = None):
        for field_info in fields(self):
            field_role = field_info.metadata.get(PERSISTENCE_ROLE_KEY)
            if field_role is None:
                continue
            if role is not None and field_role != role:
                continue
            yield field_info

    def _collect_declared_artifacts(self) -> list[ArtifactRecord]:
        artifacts : list[ArtifactRecord] = []
        for field_info in self._iter_persistence_fields(PersistenceRole.ARTIFACT.value):
            value = getattr(self, field_info.name)
            if value is None:
                continue
            values = value if isinstance(value, (list, tuple, set)) else [value]
            for item in values:
                if item is None:
                    continue
                artifacts.append(
                    ArtifactRecord(
                        name=field_info.metadata.get(ARTIFACT_NAME_KEY, field_info.name.lstrip("_")),
                        path=str(Path(item)),
                        kind=field_info.metadata.get(ARTIFACT_KIND_KEY, "artifact"),
                        policy=field_info.metadata.get(ARTIFACT_POLICY_KEY, ArtifactPolicy.DURABLE.value),
                        managed=field_info.metadata.get(ARTIFACT_MANAGED_KEY, True),
                        metadata={"field_name": field_info.name},
                    )
                )
        return artifacts

    def _restore_declared_artifact_fields(self, artifact_payloads: list[dict[str, Any]] | None):
        if artifact_payloads is None:
            return
        for field_info in self._iter_persistence_fields(PersistenceRole.ARTIFACT.value):
            matching_paths = [
                item.get("path")
                for item in artifact_payloads
                if item.get("metadata", {}).get("field_name") == field_info.name
            ]
            if not matching_paths:
                continue
            if isinstance(getattr(self, field_info.name), (list, tuple, set)):
                setattr(self, field_info.name, list(matching_paths))
            else:
                setattr(self, field_info.name, matching_paths[0])

    def _dedupe_artifacts(self, artifacts: list[ArtifactRecord]) -> list[ArtifactRecord]:
        deduped : list[ArtifactRecord] = []
        seen : set[tuple[str, str, str]] = set()
        for artifact in artifacts:
            key = (artifact.name, artifact.path, artifact.kind)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(artifact)
        return deduped

    def _snapshot_copy(self, value: Any):
        try:
            return copy.deepcopy(value)
        except Exception:
            return value

    def _uses_custom_persistence_overrides(self) -> bool:
        cls = self.__class__
        return any(
            [
                cls.snapshot_state is not AgentElement.snapshot_state,
                cls.restore_state is not AgentElement.restore_state,
                cls.save_owned_artifacts is not AgentElement.save_owned_artifacts,
                cls.load_owned_artifacts is not AgentElement.load_owned_artifacts,
            ]
        )

    def _validate_persistence_schema(self):
        missing : list[str] = []
        for field_info in fields(self):
            if field_info.name in {"type", "id", "load_on_install", "uid"}:
                continue
            if field_info.metadata.get("config") is True or "description" in field_info.metadata:
                continue
            if field_info.metadata.get(PERSISTENCE_ROLE_KEY) is not None:
                continue
            if field_info.init is False and field_info.name.startswith("_"):
                missing.append(field_info.name)
        if missing and not self._uses_custom_persistence_overrides():
            raise ValueError(
                f"{self.__class__.__name__} defines runtime dataclass fields without persistence roles: {', '.join(missing)}"
            )
