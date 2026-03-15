from __future__ import annotations
import json
import shutil
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
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
)
from ..utils.ClassUtils import ClassUtils
from ..utils.FileUtils import FileUtils

if TYPE_CHECKING:
    from .Agent import Agent
    
@dataclass
class AgentElement(ABC):
    """
    Abstract base class for agent elements.
    """

    type : str = field(default=None, metadata={"description": "fully qualified package and class name descriptor"})
    id : str = field(default=None, metadata = {"description": "unique identifier of element in DataGrabber application"})
    load_on_install : bool = field(default=False, metadata = {"description": "specifies whether the GrabberElement should try to load from local json config file on install"})
    uid : str = field(default=None)
      
    def __post_init__(self):
        """
        Initialize the agent element and assign a unique ID.
        """
        self.type = self.__module__                   
        if self.id is None: 
            self.id = self.unique_id()
        if self.uid is None:
            self.uid = uuid.uuid4().hex
        self._state : AgentElementState = AgentElementState.UNINSTALLED
        self._managed_artifacts : list[ArtifactRecord] = []
        
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
            self.load()
        self._on_install(agent)
        self._state = AgentElementState.INSTALLED
        
    def uninstall(self, agent : Agent = None):
        """resets the element, this method can be used to stop internal element logic or reset objects that were initialized on creation
        """
        self._on_uninstall(agent)
        self._state = AgentElementState.UNINSTALLED
        return
    
    def load(self):
        self.load_config(self._legacy_config_path())
    
    def save(self):
        self.save_config(self._legacy_config_path())
            
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
            return True
        logger.warning("no configuration file " + str(target) + " to load from was found")
        return False

    def snapshot_state(self) -> dict:
        return {}

    def restore_state(self, payload: dict | None):
        return

    def list_owned_artifacts(self) -> list[ArtifactRecord]:
        return list(self._managed_artifacts)

    def save_owned_artifacts(self, checkpoint_id: str | None = None, agent: Agent = None):
        return

    def load_owned_artifacts(self, snapshot: dict | None = None, agent: Agent = None):
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
        self.save_owned_artifacts(agent=agent)
        artifacts = self.list_owned_artifacts()
        state_value = self._state.value if hasattr(self._state, "value") else str(self._state)
        return ElementSnapshot(
            uid=self.uid,
            id=self.id,
            type=self.type,
            state=state_value,
            payload=self.snapshot_state(),
            artifacts=artifacts,
        )

    def restore_from_snapshot(self, snapshot: dict | None, agent: Agent = None) -> bool:
        if snapshot is None:
            return False
        self.restore_state(snapshot.get("payload", {}))
        self.load_owned_artifacts(snapshot=snapshot, agent=agent)
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

    def get_artifact_root(self, agent: Agent = None) -> Path:
        storage = self.get_runtime_storage(agent)
        root = storage.artifacts_root / self.__class__.__name__ / self.uid
        FileUtils.create_dir(str(root))
        return root

    def _runtime_owner_uid(self, agent: Agent = None) -> str:
        if agent is not None and hasattr(agent, "uid"):
            return agent.uid
        agent_ref = getattr(self, "_agent", None)
        if agent_ref is not None and hasattr(agent_ref, "uid"):
            return agent_ref.uid
        return self.uid

    def _default_config_path(self, agent: Agent = None) -> Path:
        storage = self.get_runtime_storage(agent)
        target = storage.config_root / "elements" / f"{self.uid}.json"
        FileUtils.create_dir(str(target.parent))
        return target

    def _legacy_config_path(self) -> Path:
        return Path(self.id + ".json")

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
