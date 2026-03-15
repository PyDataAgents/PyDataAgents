from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterator
import uuid

from ..utils.FileUtils import FileUtils
from ..utils.TimeUtils import TimeUtils


class CleanupScope(str, Enum):
    TMP_ONLY = "tmp-only"
    REBUILDABLE_OWNER_CACHE = "rebuildable-owner-cache"
    RUNTIME_ORPHANED_ARTIFACTS = "runtime-orphaned-artifacts"
    CHECKPOINT_RETENTION_PRUNING = "checkpoint-retention-pruning"
    SHARED_CACHE_PRUNE = "shared-cache-prune"


class ArtifactPolicy(str, Enum):
    EPHEMERAL = "ephemeral"
    REBUILDABLE = "rebuildable"
    DURABLE = "durable"
    SHARED = "shared"


@dataclass
class ArtifactRecord:
    name: str
    path: str
    kind: str = "artifact"
    policy: str = ArtifactPolicy.DURABLE.value
    managed: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ElementSnapshot:
    uid: str
    id: str
    type: str
    state: str | None
    payload: dict[str, Any] = field(default_factory=dict)
    artifacts: list[ArtifactRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data


@dataclass
class CheckpointManifest:
    checkpoint_id: str
    agent_uid: str
    agent_id: str
    created_at: int
    lifecycle_state: str | None
    run_id: str | None
    element_files: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CleanupReport:
    scope: str
    dry_run: bool
    deleted: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    candidates: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _json_default(value: Any):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "tolist"):
        return value.tolist()
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return str(value)


class RuntimeStorage:
    """Shared runtime filesystem and metadata helper for a single agent."""

    def __init__(self, agent_uid: str, resource_root: str | Path = "./resources/"):
        self.agent_uid = str(agent_uid)
        self.resource_root = Path(resource_root)
        self.runtime_root = self.resource_root / "runtime" / self.agent_uid
        self.config_root = self.runtime_root / "config"
        self.db_root = self.runtime_root / "db"
        self.checkpoints_root = self.runtime_root / "checkpoints"
        self.artifacts_root = self.runtime_root / "artifacts"
        self.spool_root = self.runtime_root / "spool"
        self.logs_root = self.runtime_root / "logs"
        self.tmp_root = self.runtime_root / "tmp"
        self.db_path = self.db_root / "state.sqlite3"
        self.current_checkpoint_path = self.runtime_root / "current_checkpoint.json"

    def ensure_layout(self):
        for path in (
            self.resource_root,
            self.runtime_root,
            self.config_root,
            self.db_root,
            self.checkpoints_root,
            self.artifacts_root,
            self.spool_root,
            self.logs_root,
            self.tmp_root,
        ):
            FileUtils.create_dir(str(path))
        self._initialize_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        self.ensure_layout()
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runtime_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    created_at INTEGER NOT NULL,
                    lifecycle_state TEXT,
                    manifest_path TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    started_at INTEGER NOT NULL,
                    stopped_at INTEGER
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS dedupe_keys (
                    dedupe_key TEXT PRIMARY KEY,
                    created_at INTEGER NOT NULL,
                    metadata TEXT
                )
                """
            )

    def write_json(self, path: str | Path, payload: dict[str, Any]):
        path = Path(path)
        FileUtils.create_dir(str(path.parent))
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=4, default=_json_default)

    def read_json(self, path: str | Path, default: Any = None) -> Any:
        path = Path(path)
        if not path.exists():
            return default
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def save_agent_config(self, payload: dict[str, Any]):
        self.write_json(self.config_root / "agent.json", payload)

    def load_agent_config(self) -> dict[str, Any] | None:
        return self.read_json(self.config_root / "agent.json")

    def create_checkpoint_id(self) -> str:
        return f"checkpoint-{TimeUtils.utc_ms()}-{uuid.uuid4().hex[:8]}"

    def create_checkpoint_dir(self, checkpoint_id: str) -> Path:
        checkpoint_dir = self.checkpoints_root / checkpoint_id
        FileUtils.create_dir(str(checkpoint_dir / "elements"))
        return checkpoint_dir

    def element_snapshot_path(self, checkpoint_id: str, element_uid: str) -> Path:
        return self.checkpoints_root / checkpoint_id / "elements" / f"{element_uid}.json"

    def write_element_snapshot(self, checkpoint_id: str, snapshot: ElementSnapshot):
        path = self.element_snapshot_path(checkpoint_id, snapshot.uid)
        self.write_json(path, snapshot.to_dict())
        return path

    def load_element_snapshot(self, checkpoint_id: str, element_uid: str) -> dict[str, Any] | None:
        return self.read_json(self.element_snapshot_path(checkpoint_id, element_uid))

    def manifest_path(self, checkpoint_id: str) -> Path:
        return self.checkpoints_root / checkpoint_id / "manifest.json"

    def write_manifest(self, manifest: CheckpointManifest):
        self.write_json(self.manifest_path(manifest.checkpoint_id), manifest.to_dict())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO checkpoints(checkpoint_id, created_at, lifecycle_state, manifest_path)
                VALUES(?, ?, ?, ?)
                """,
                (
                    manifest.checkpoint_id,
                    manifest.created_at,
                    manifest.lifecycle_state,
                    str(self.manifest_path(manifest.checkpoint_id)),
                ),
            )
        self.set_current_checkpoint(manifest.checkpoint_id)

    def load_manifest(self, checkpoint_id: str) -> dict[str, Any] | None:
        return self.read_json(self.manifest_path(checkpoint_id))

    def list_checkpoints(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT checkpoint_id FROM checkpoints ORDER BY created_at DESC"
            ).fetchall()
        return [row[0] for row in rows]

    def set_runtime_value(self, key: str, value: Any):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO runtime_state(key, value) VALUES(?, ?)",
                (key, json.dumps(value, default=_json_default)),
            )

    def get_runtime_value(self, key: str, default: Any = None) -> Any:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM runtime_state WHERE key = ?",
                (key,),
            ).fetchone()
        if row is None:
            return default
        return json.loads(row[0])

    def set_current_checkpoint(self, checkpoint_id: str | None):
        payload = {"checkpoint_id": checkpoint_id}
        self.write_json(self.current_checkpoint_path, payload)
        self.set_runtime_value("current_checkpoint", checkpoint_id)

    def get_current_checkpoint(self) -> str | None:
        data = self.read_json(self.current_checkpoint_path)
        if isinstance(data, dict) and "checkpoint_id" in data:
            return data["checkpoint_id"]
        return self.get_runtime_value("current_checkpoint")

    def set_lifecycle_state(self, lifecycle_state: str):
        self.set_runtime_value("lifecycle_state", lifecycle_state)

    def get_lifecycle_state(self, default: str | None = None) -> str | None:
        return self.get_runtime_value("lifecycle_state", default)

    def start_run(self) -> str:
        run_id = f"run-{TimeUtils.utc_ms()}-{uuid.uuid4().hex[:8]}"
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO runs(run_id, started_at, stopped_at) VALUES(?, ?, ?)",
                (run_id, TimeUtils.utc_ms(), None),
            )
        self.set_runtime_value("current_run_id", run_id)
        return run_id

    def stop_run(self, run_id: str | None):
        if run_id is None:
            return
        with self._connect() as conn:
            conn.execute(
                "UPDATE runs SET stopped_at = ? WHERE run_id = ?",
                (TimeUtils.utc_ms(), run_id),
            )
        if self.get_runtime_value("current_run_id") == run_id:
            self.set_runtime_value("current_run_id", None)

    def get_current_run_id(self) -> str | None:
        return self.get_runtime_value("current_run_id")

    def runtime_tmp_paths(self) -> list[Path]:
        if not self.tmp_root.exists():
            return []
        return list(self.tmp_root.iterdir())
