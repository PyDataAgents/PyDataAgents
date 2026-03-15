# Technical Reference

This document is the low-level engineering reference for the repository. It is intentionally more detailed than the main README and is meant to be useful to both humans and LLM-based tooling that need to understand how the framework works internally.

The current focus of this document is the Stage 1 resilient runtime foundation that was added around agent lifecycle control, runtime persistence, checkpoints, cleanup, and restart behavior. The file is designed to grow over time with additional detailed technical notes.

## Purpose

Use this document when you need to understand:

- how a single `Agent` runtime persists and restores state
- where restart and checkpoint logic lives in the class hierarchy
- how runtime files are laid out under `resources/runtime/...`
- which parts of restart behavior are shared by the framework and which remain local to concrete elements
- what is currently crash-tolerant, what is only cooperative, and what is still planned

Repository anchors for the mechanics described here:

- `pydag/agents/Agent.py`
- `pydag/agents/AgentElement.py`
- `pydag/agents/RuntimeStorage.py`
- `pydag/agents/AgentStates.py`
- `pydag/services/Service.py`
- `pydag/services/ObserverThread.py`
- `pydag/services/rest/RestService.py`
- `pydag/services/rest/AgentRESTAPI.py`
- `pydag/nodes/Node.py`
- `pydag/nodes/LearningNode.py`
- `pydag/buffers/Buffer.py`
- `pydag/adapters/Adapter.py`

## Scope And Current Maturity

The current implementation is a Stage 1 runtime foundation.

What is implemented now:

- one supervised `Agent` per runtime
- stable runtime storage rooted by an immutable `uid`
- explicit aggregate lifecycle states
- config persistence separated from runtime checkpoint persistence
- per-element snapshots coordinated by the `Agent`
- restart from the latest valid checkpoint
- cleanup hooks and checkpoint pruning
- in-runtime REST endpoints for runtime control

What is intentionally not implemented yet:

- an external multi-runtime registry that starts and stops agents by `agent_id`
- distributed orchestration
- a full transactional outbox or exactly-once side-effect framework
- automatic rollback of already emitted external side effects
- a full orphan-artifact graph sweeper

This matters for the phrase "fail-safe restart logic". In the current repo, "fail-safe" means the runtime is designed to preserve and restore a last known good checkpoint and avoid corrupting the checkpoint pointer during partial writes. It does not yet mean exactly-once delivery or full distributed recovery semantics.

## Architectural Invariants

The runtime logic follows a few hard rules.

### One Agent Per Runtime

Each process supervises exactly one `Agent`. The runtime does not contain an in-process scheduler for multiple agents. If multiple agents run in parallel, they must run in separate scripts, services, or OS-level supervision units.

### Shared Logic Lives High In The Hierarchy

Shared persistence and lifecycle policy lives as high as possible:

- `AgentElement` defines the common persistence and cleanup contract
- `Agent` coordinates aggregate lifecycle and checkpoints
- `Service`, `Node`, `Buffer`, `Adapter`, and `LearningNode` add shared specialization

This reduces leaf-class duplication and limits downstream churn when the framework evolves.

### Artifact Semantics Stay With The Owner

The framework decides where runtime state and artifacts are stored and how checkpoint metadata is written. The concrete owning object decides:

- which artifacts it owns
- whether they are valid or stale
- whether they can be reused
- whether they must be rebuilt
- whether they are safe to clean up

This rule applies to all persisted objects, not only vector stores.

## Runtime Identity Model

Two identifiers now matter:

- `id`: human-facing identifier used across the existing framework and APIs
- `uid`: stable machine-oriented identifier used for runtime paths, checkpoint files, and future registry keys

Both `Agent` and `AgentElement` now have a `uid`.

Why `uid` exists:

- `id` values are human-readable and may contain spaces or user-defined text
- runtime directories need a filesystem-safe stable key
- future external lifecycle control needs a durable key that is independent from presentation

Current runtime identifiers in practice:

- `Agent.uid` identifies the runtime storage root
- `AgentElement.uid` identifies element snapshots inside a checkpoint
- `run_id` identifies a running release cycle inside the runtime metadata store
- `checkpoint_id` identifies a checkpoint directory and manifest
- `Node._execution_id` identifies a node execution attempt

## Aggregate Agent Lifecycle

The aggregate runtime lifecycle is defined in `pydag/agents/AgentStates.py` through `AgentLifecycleState`.

States currently implemented:

- `CREATED`
- `READY`
- `RUNNING`
- `PAUSING`
- `PAUSED`
- `QUIESCING`
- `CHECKPOINTING`
- `RESTORING`
- `STOPPING`
- `STOPPED`
- `FAILED`

Intended meanings:

- `CREATED`: agent object exists, runtime storage may already exist, but the runtime is not active
- `READY`: elements are installed and the agent is structurally prepared to run
- `RUNNING`: adapters are connected, auto-start services are started, runtime is active
- `PAUSING`: transient control state while pausing services
- `PAUSED`: runtime is logically paused
- `QUIESCING`: runtime is draining toward a safe checkpoint or restore boundary
- `CHECKPOINTING`: coordinated snapshot is being created
- `RESTORING`: a checkpoint is being loaded
- `STOPPING`: runtime is shutting down
- `STOPPED`: runtime is not active and all installed elements should be uninstalled
- `FAILED`: reserved for hard runtime failure states

The `Agent` persists the aggregate lifecycle state into runtime metadata every time `_set_lifecycle_state(...)` is called.

## Runtime Storage Layout

The Stage 1 storage contract is implemented by `pydag/agents/RuntimeStorage.py`.

The runtime root is:

```text
resources/runtime/<agent_uid>/
```

The current substructure is:

```text
resources/runtime/<agent_uid>/
  config/
    agent.json
    elements/
  db/
    state.sqlite3
  checkpoints/
    <checkpoint_id>/
      manifest.json
      elements/
        <element_uid>.json
  artifacts/
    <ElementClass>/
      <element_uid>/
  spool/
  logs/
  tmp/
  current_checkpoint.json
```

The storage split is deliberate.

- JSON files are used for readable snapshots and manifests
- filesystem directories are used for larger owner-managed artifacts
- SQLite is used only for runtime index and metadata records

SQLite currently stores:

- lifecycle state
- current checkpoint id
- current run id
- checkpoint inventory
- run start and stop timestamps
- placeholder dedupe key records for later stages

This is a hybrid design. Bulk element payloads and artifacts are not stored inside SQLite.

## Why `RuntimeStorage` Is A Peer Module Under `pydag/agents`

`RuntimeStorage` is not just a private helper inside `Agent`.

It sits under `pydag/agents` because it defines shared runtime concepts used by both `Agent` and `AgentElement`, including:

- `CleanupScope`
- `ArtifactPolicy`
- `ArtifactRecord`
- `ElementSnapshot`
- `CheckpointManifest`
- `CleanupReport`

That placement matters architecturally. If runtime storage were hidden as a private helper inside `Agent`, element-level persistence would be forced to reach into `Agent` internals. The current location keeps persistence as a first-class concern of the agent subsystem rather than a private detail of one class.

If this area grows substantially later, a future `pydag/runtime/` or `pydag/persistence/` package may become cleaner. For the current codebase, keeping it as a shared module under `pydag/agents` is the correct intermediate design.

## Config Persistence Versus Runtime Persistence

The implementation now separates two different concerns.

### Config Persistence

Config persistence captures structural configuration that can be reloaded independently from runtime execution.

Current entry points:

- `Agent.save_config(...)`
- `Agent.load_config(...)`
- `AgentElement.save_config(...)`
- `AgentElement.load_config(...)`

Compatibility wrappers still exist:

- `AgentElement.save()`
- `AgentElement.load()`

Those wrappers now delegate to config persistence but preserve the older calling convention.

### Runtime Persistence

Runtime persistence captures logical execution state that matters for restart and recovery.

Current entry points:

- `Agent.checkpoint(...)`
- `Agent.restore(...)`
- `Agent.reload_current()`
- `AgentElement.checkpoint(...)`
- `AgentElement.restore(...)`

This distinction is important. A config file is not a restart snapshot. A checkpoint is not just configuration.

## The Element Snapshot Contract

The framework-level persistence contract now lives in `AgentElement`.

Shared methods introduced or formalized there:

- `save_config(...)`
- `load_config(...)`
- `snapshot_state()`
- `restore_state(payload)`
- `list_owned_artifacts()`
- `save_owned_artifacts(...)`
- `load_owned_artifacts(...)`
- `validate_restored_state(...)`
- `build_snapshot(...)`
- `restore_from_snapshot(...)`
- `checkpoint(...)`
- `restore(...)`
- `cleanup(...)`
- `cleanup_dry_run(...)`
- `get_runtime_storage(...)`
- `get_runtime_root(...)`
- `get_state_root(...)`
- `get_artifact_root(...)`

The contract is layered by design.

What the base class owns:

- path resolution
- snapshot envelope structure
- config path defaults
- artifact registration
- generic cleanup dispatch
- restore-state enum conversion

What the concrete element still owns:

- the logical payload inside `snapshot_state()`
- the interpretation of that payload inside `restore_state(...)`
- the artifact list it returns or registers
- whether an artifact should be reused or rebuilt
- how an artifact is recreated after restore

This is the core framework rule: policy is centralized high in the hierarchy, semantics remain local to the owner.

## What Counts As Serializable State

Safe to serialize now:

- dataclass configuration values
- buffer contents and related logical metadata
- node execution metadata
- service heartbeat and pause state
- adapter side-effect receipt records
- learning-model descriptors
- runtime file paths and artifact descriptors
- data-model instance values that can be converted to dictionaries

Not safe to serialize directly:

- threads
- thread locks
- network sockets
- live database connections
- live REST server instances
- live Chroma objects
- live LLM SDK clients
- loaded Python modules with active interpreter state

The restart contract is therefore cooperative and reconstructive:

- serialize logical state
- re-create live runtime handles from configuration and descriptors

## Fail-Safe Checkpoint Mechanics

The fail-safe restart behavior starts with how checkpoints are written.

### Checkpoint Goals

The checkpoint path is designed to:

- preserve the last valid checkpoint if a new checkpoint fails mid-write
- separate per-element state from the aggregate manifest
- keep checkpoint payloads inspectable on disk
- avoid storing live process objects

### Checkpoint Flow In `Agent.checkpoint(...)`

Current flow:

1. Ensure runtime storage layout exists.
2. Persist the current agent configuration to `config/agent.json`.
3. Choose a new `checkpoint_id` if none was supplied.
4. Capture the pre-checkpoint lifecycle state.
5. If the agent is actively running, quiesce it first.
6. Set lifecycle state to `CHECKPOINTING`.
7. Create the checkpoint directory and its `elements/` subdirectory.
8. Iterate over `Agent.get_all_elements()`.
9. Ask each element to produce a checkpoint snapshot through `element.checkpoint(agent=self)`.
10. Write one JSON snapshot file per element, keyed by element `uid`.
11. Build a `CheckpointManifest` that records aggregate metadata and the per-element snapshot file map.
12. Write the manifest to `checkpoints/<checkpoint_id>/manifest.json`.
13. Register the checkpoint in SQLite metadata.
14. Update `current_checkpoint.json` and the runtime metadata pointer only after the manifest write succeeds.
15. Resume the runtime if it was running before checkpointing. Otherwise restore the prior lifecycle state.

The key safety property is that the manifest and current-checkpoint pointer are written after the element snapshot files. A half-written checkpoint therefore does not replace the previous current checkpoint.

### What This Protects Against

This design protects reasonably well against:

- process death before the manifest is written
- process death before the current checkpoint pointer is advanced
- partial creation of a new checkpoint directory while an older checkpoint remains valid

### What This Does Not Fully Protect Against Yet

This Stage 1 design does not yet provide:

- atomic multi-file commit across all artifact writes
- rollback of owner-written artifacts if an element fails mid-checkpoint
- exactly-once side-effect guarantees across external systems
- supervisor-level automatic re-run policy after a crash

That is why owner-level artifact logic still matters. If a concrete element writes mutable artifacts during checkpointing, it must do so in a way that tolerates interruption or can be validated and rebuilt later.

## Fail-Safe Restore And Reload Mechanics

Restore logic is the second half of the fail-safe restart model.

### Restore Flow In `Agent.restore(...)`

Current flow:

1. Resolve the target checkpoint id, defaulting to the current checkpoint pointer.
2. Load the checkpoint manifest.
3. If no manifest exists, return `False`.
4. Capture the prior lifecycle state.
5. If the agent is running, quiesce it first.
6. Set lifecycle state to `RESTORING`.
7. Iterate over all current elements.
8. Load each element snapshot by element `uid`.
9. Call `element.restore(snapshot=snapshot, agent=self)` for each present snapshot.
10. If the runtime was actively running before restore, resume it.
11. Otherwise restore the lifecycle value recorded in the manifest, or fall back to the prior state.

This flow is restart-safe only if the element graph is structurally compatible with the stored checkpoint. In Stage 1, checkpoint restore assumes the same logical agent composition is present when restore is called.

### Reload Flow In `Agent.reload_current()`

`reload_current()` is intentionally simple:

1. create a fresh checkpoint
2. restore from that new checkpoint

This is useful as a local consistency test of the snapshot contract and as a controlled "soft restart" of the in-memory runtime state.

### Why Restore Is Cooperative

Restore does not recreate the entire process image. It restores logical state into already-instantiated objects. This means:

- element constructors still matter
- install-time object wiring still matters
- owner-specific `restore_state(...)` logic must be conservative

This also means there is no magic process checkpointing. If a service needs live handles back after restore, it must recreate them from config or descriptors when it next starts.

## Pause, Quiesce, And Stop Semantics

The restart logic relies on services participating cooperatively.

### Service-Level Control

`pydag/services/Service.py` now adds:

- `_pause_event`
- `_quiesce_event`
- `_stop_event`
- `_heartbeat_ts`
- `pause()`
- `resume()`
- `quiesce()`
- `heartbeat()`
- snapshot and restore support for the control flags

The framework expectation is:

- `pause()` temporarily suppresses active work
- `quiesce()` moves the service toward a safe checkpoint boundary and implies pause
- `stop()` ends the service

### Observer Threads

`ObserverThread` was updated to cooperate with the new service controls:

- `notify_observers()` now checks `service.is_paused()`
- paused services back off briefly instead of continuing normal work
- the thread joins on terminate
- heartbeat timestamps are refreshed during notify cycles

This improves restart coordination, but it is still cooperative. A service that ignores its own pause or quiesce state can still weaken checkpoint consistency.

### REST Service Shutdown

`RestService` now uses a stoppable `uvicorn.Server` object instead of a fire-and-forget `uvicorn.run()` call. This matters because `stop()` and future reload control depend on the REST server actually being stoppable from inside the process.

## Shared Element Specializations

The Stage 1 runtime pushes common restart and persistence behavior upward into the hierarchy.

### `Buffer`

`Buffer.snapshot_state()` now serializes:

- the logical buffer contents
- last access timestamps
- timer metadata

`Buffer.restore_state(...)` restores those logical values directly.

This is the simplest example of restartable logical state.

### `Adapter`

`Adapter.snapshot_state()` now serializes:

- side-effect receipt records

This is groundwork for safer recovery later. It is not yet a full idempotency system.

### `Node`

`Node.snapshot_state()` now serializes:

- activation status
- last execution timestamp
- current execution id
- last transition timestamp
- retry marker
- interrupted flag

`Node.record_output_artifact(...)` lets nodes register generated files as tracked artifacts or side effects without implying that they are fully managed checkpoint payloads.

### `LearningNode`

`LearningNode.snapshot_state()` now serializes:

- whether the node still requires learning
- model descriptors produced by `_serialize_models()`

This intentionally avoids trying to serialize live model objects.

## Owner-Local Artifact Policy

The new runtime contract deliberately does not centralize artifact semantics.

### Rule

The framework controls:

- the artifact root
- checkpoint metadata
- snapshot file location
- cleanup dispatch

The owning element controls:

- whether an artifact exists
- whether it is valid
- whether it should be reused
- whether it should be rebuilt
- how it should be loaded again

### Concrete Examples In The Current Repo

`RAGService`:

- resolves its own vector-store directory through `_resolve_vector_store_directory()`
- defaults to the agent runtime artifact root when installed in an agent and no path is configured
- keeps existing explicit path semantics when configured directly
- registers the resolved vector store as a durable artifact

`FileEmbeddingService`:

- resolves its embedding-store directory itself
- preserves standalone compatibility with the legacy shared path under `resources/embeddings/...`
- uses the agent runtime artifact root when installed in an agent
- registers the embedding store as a durable artifact

`DataModelService`:

- snapshots model instance values into plain dictionaries
- recreates fresh data-model instances on restore and reapplies values
- intentionally does not try to serialize Python execution state or live locks

`WritePDFFormAction`:

- records written PDF output paths as output artifacts through `Node.record_output_artifact(...)`
- treats produced files as outputs and side effects, not as blindly inlined checkpoint state

This owner-local rule is framework-wide. The RAG case is only one example of the general design.

## Cleanup Model

Cleanup is now part of the lifecycle model rather than scattered ad hoc deletion logic.

### Cleanup Scopes

`CleanupScope` currently defines:

- `tmp-only`
- `rebuildable-owner-cache`
- `runtime-orphaned-artifacts`
- `checkpoint-retention-pruning`
- `shared-cache-prune`

Not all scopes are fully implemented yet.

### Artifact Policies

`ArtifactPolicy` currently defines:

- `ephemeral`
- `rebuildable`
- `durable`
- `shared`

The intent is:

- `ephemeral`: safe temporary files
- `rebuildable`: safe to delete and regenerate
- `durable`: active runtime state that should be preserved
- `shared`: reusable cross-agent cache that should only be pruned deliberately

### Current `AgentElement.cleanup(...)` Behavior

The base cleanup implementation:

- enumerates artifacts from `list_cleanup_targets()`
- filters them by scope and artifact policy
- supports dry-run reporting
- deletes directories or files for matching entries when not in dry-run mode

### Current `Agent.cleanup(...)` Behavior

The aggregate cleanup layer currently adds:

- element cleanup aggregation
- runtime `tmp/` cleanup
- checkpoint retention pruning

Checkpoint pruning currently preserves the current checkpoint when pruning by count.

### Important Limitation

`runtime-orphaned-artifacts` and `shared-cache-prune` are design-level scopes today, but they are not yet implemented as a full reference-graph and safety-check system. Operators and developers should treat those scopes as planned extension points rather than complete production-grade cleanup automation.

## REST Control Surface

The in-runtime management surface is currently exposed through `AgentRESTAPI`.

Implemented Stage 1 endpoints:

- `GET /api/v1/agent/status`
- `POST /api/v1/agent/pause`
- `POST /api/v1/agent/resume`
- `POST /api/v1/agent/checkpoint`
- `POST /api/v1/agent/reload`
- `POST /api/v1/agent/cleanup`

These endpoints act only on the currently loaded runtime agent. They are not a fleet manager and they do not violate the one-agent-per-runtime rule.

## Current Failure Model And Guarantees

The current restart logic offers practical local resilience, but it is important to be precise about the guarantees.

### What Is Strong Today

- the runtime root is deterministic and stable
- lifecycle state is persisted outside process memory
- checkpoint manifests are written after element snapshots
- the current checkpoint pointer is updated after manifest write
- logical buffer, node, service, adapter, and model state can be restored
- the runtime can perform a local checkpoint-and-reload cycle

### What Is Moderate Today

- restart consistency depends on elements obeying the snapshot contract
- restart consistency depends on services cooperating with pause and quiesce
- artifact recovery quality depends on owner-local validation and rebuild logic

### What Is Weak Or Deferred Today

- external side-effect deduplication is still partial
- durable artifact writes are not globally transactional
- there is no external registry-driven restart manager yet
- there is no full process supervisor policy inside the repo itself
- there is no automatic undo for outputs already written to external systems

## Operational Implications

When extending the repo, keep these operational rules in mind.

### If You Add A New Element Type

Implement the smallest amount of custom persistence possible.

Prefer to override:

- `snapshot_state()`
- `restore_state(...)`
- `list_owned_artifacts()` or `register_artifact(...)`
- `save_owned_artifacts(...)`
- `load_owned_artifacts(...)`
- `validate_restored_state(...)`

Do not duplicate runtime path logic in leaf classes unless there is a strong owner-specific reason.

### If You Add A New Artifact Type

Keep the rule split intact:

- shared storage policy belongs in the base classes
- artifact validity and rebuild logic belongs in the owner

### If You Add A New Long-Running Service

Make sure it cooperates with:

- `pause()`
- `quiesce()`
- `stop()`
- `heartbeat()`

If it uses its own loop or worker thread, ensure those controls are actually checked.

## Test Coverage

The runtime foundation is covered primarily by:

- `tests/unit/agents/test_agent.py`
- `tests/unit/services/test_runtime_persistence.py`

The `test_agent.py` coverage includes the new aggregate runtime methods and runtime-control API behavior, including:

- lifecycle state reads and writes
- config save and load
- pause, resume, and quiesce
- checkpoint and restore
- reload
- cleanup
- runtime status reporting
- runtime REST endpoints

Tests are important here because restart logic is easy to make plausible and easy to get subtly wrong.

## Known Limitations And Tradeoffs

The Stage 1 design makes a few deliberate tradeoffs.

### Hybrid Persistence Instead Of Full Event Sourcing

The repo uses snapshots plus lightweight SQLite metadata rather than a full append-only event journal. This is simpler to inspect and integrate with the current codebase, but it gives up some replay power and audit richness.

### Cooperative Quiesce Instead Of Forced Preemption

Python services and observer threads are paused cooperatively. This keeps the design simple and compatible with the current architecture, but it means element implementations must behave correctly for checkpoints to be truly consistent.

### Human-Readable JSON Over Opaque Binary State

Element snapshots are JSON files. This is useful for debugging and tooling, but large or highly structured runtime states may eventually need more specialized storage.

### Local Runtime First

The current design is intentionally optimized for a single process on one machine with a local `resources/runtime/...` tree. Multi-host coordination is a later stage.

## Planned Next Extensions

The runtime persistence layer was designed with a later Stage 2 in mind.

Expected next additions:

- external saved-agent registry
- `start/stop/reload/delete/cleanup` by runtime agent identifier
- registry metadata under `resources/registry/agents/...`
- stronger dedupe and side-effect recovery records
- richer orphan-artifact detection
- deeper operational diagnostics and health reporting

Those features should build on the current `uid`, checkpoint manifest, lifecycle metadata, and runtime-root conventions rather than replacing them.

## Quick Mental Model

The shortest accurate mental model of the current implementation is:

An `Agent` is a composition and lifecycle coordinator for one runtime. Each `AgentElement` owns its logical state and any artifact semantics it understands. `RuntimeStorage` provides the shared runtime filesystem and metadata index. A checkpoint is a coordinated set of element snapshots plus one manifest written last. A restore rehydrates logical state into already-instantiated objects and then relies on owners to recreate live resources safely. Cleanup is policy-driven and still conservative. External fleet-style lifecycle control is intentionally deferred to a later stage.
