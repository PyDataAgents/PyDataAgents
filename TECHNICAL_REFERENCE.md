# Technical Reference

This document is the low-level engineering reference for the repository. It is intentionally more detailed than the main README and is meant to be useful to both humans and LLM-based tooling that need to understand how the framework works internally.

The current focus of this document is the Stage 1 resilient runtime foundation that was added around agent lifecycle control, runtime persistence, checkpoints, cleanup, and restart behavior. The file is designed to grow over time with additional detailed technical notes.

## Purpose

Use this document when you need to understand:

- how a single `Agent` runtime persists and restores state
- where restart and checkpoint logic lives in the class hierarchy
- how runtime files are laid out under `resources/runtime/...`
- how shared long-lived artifacts are laid out under `resources/...`
- which parts of restart behavior are shared by the framework and which remain local to concrete elements
- what is currently crash-tolerant, what is only cooperative, and what is still planned

If you are new to the project, read this document in this order:

1. `Architectural Invariants`
2. `Runtime Storage Layout`
3. `Agent Runtime Versus Shared Resource Roots`
4. `Fail-Safe Checkpoint Mechanics`
5. `Fail-Safe Restore And Reload Mechanics`
6. `Shared Element Specializations`
7. `How To Build A New Element`

That path is the shortest route from "what does the runtime do?" to "how do I extend it safely?".

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
- stable runtime storage rooted by a deterministic `uid`
- explicit aggregate lifecycle states
- config persistence separated from runtime checkpoint persistence
- per-element snapshots coordinated by the `Agent`
- exact-match startup auto-resume from the latest valid checkpoint
- automatic checkpoints coordinated by the `Agent`
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

### Deterministic Default `uid` Derivation

The default `uid` model is now deterministic rather than random.

If a caller does not explicitly provide a `uid`:

- `Agent.uid` is derived from a normalized form of `Agent.id`
- top-level buffers derive `buffer/<normalized-id>`
- top-level adapters derive `adapter/<normalized-id>`
- top-level services derive `service/<normalized-id>`
- statemachine nodes derive their `uid` from their service ownership scope plus their node id

This matters because restart behavior depends on stable identity. A new process should derive the same runtime identity from the same logical definition without requiring the user to manually pass `uid` values every time.

Explicit `uid` override still wins. The deterministic derivation is only the default.

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

## Agent Runtime Versus Shared Resource Roots

The repository uses two storage scopes on purpose:

- agent runtime storage under `resources/runtime/<agent_uid>/...`
- shared or user-facing resource roots under `resources/...`

This split is one of the most important design rules in the current codebase. When you add a new file, cache, store, or directory, decide its scope first and only then write the code that creates it.

### Use The Agent Runtime When The Data Belongs To One Runtime

Use `resources/runtime/<agent_uid>/...` for:

- checkpoints and manifests
- runtime metadata and SQLite state
- per-run temp files, logs, and spool files
- agent-local artifacts that only make sense together with one runtime
- artifacts that should disappear when the runtime is deleted or cleaned up

Mental model:

- "this belongs to one runtime instance and its lifecycle"

Typical examples:

- checkpoint files managed by `RuntimeStorage`
- per-agent temp artifacts
- owner-local runtime state that should be cleaned together with the runtime

Developer rule:

- choose the agent runtime when the file is part of one agent's lifecycle
- choose the agent runtime when deleting the runtime should also delete the file
- choose the agent runtime when the file is part of checkpoint-owned execution state

### Use `resources/...` When The Data Should Survive One Runtime

Use the shared top-level resource roots for:

- reusable model caches under `resources/models/...`
- reusable vector stores or embedding stores under `resources/embeddings/...`
- user-provided inputs under `resources/inputs/...`
- user-facing outputs under `resources/outputs/...`
- reusable scripts or source assets under `resources/scripts/...`

Mental model:

- "this should still exist even if one runtime is deleted"

Typical examples in the current codebase:

- embedding model downloads managed through `ModelUtils`
- vector stores created by `RAGService` and `FileEmbeddingService`
- generated PDF outputs written by `PDFWriteFormAction`

Developer rule:

- choose `resources/...` when the data should still exist after one runtime is deleted
- choose `resources/...` when the data is expensive to rebuild and useful across runs
- choose `resources/...` when the data is user-facing input or output rather than checkpoint-owned runtime state

### Practical Decision Rule

When adding a new artifact, ask these questions in order:

1. If the agent runtime is deleted, should this file or directory also disappear?
   - If yes, use the agent runtime.
   - If no, use a shared `resources/...` root.

2. Is this artifact part of checkpoint-owned runtime state for exactly one agent?
   - If yes, use the agent runtime.

3. Is this expensive to rebuild and useful across restarts or later across agents?
   - If yes, prefer a shared `resources/...` root.

4. Is this user-facing input or output data?
   - If yes, use `resources/inputs/...` or `resources/outputs/...`.

This keeps restart state local while keeping durable reusable assets publicly available.

Examples:

- checkpoint manifest: `resources/runtime/<agent_uid>/checkpoints/...`
- runtime SQLite file: `resources/runtime/<agent_uid>/db/state.sqlite3`
- downloaded embedding model cache: `resources/models/...`
- durable embedding store you want to keep after one runtime is removed: `resources/embeddings/...`
- generated PDF for the user: `resources/outputs/...`

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

- `Agent.release(...)`
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
- `prepare_checkpoint(...)`
- `list_owned_artifacts()`
- `describe_additional_artifacts()`
- `save_owned_artifacts(...)`
- `load_owned_artifacts(...)`
- `rebuild_runtime_handles(...)`
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
- declarative field-role interpretation
- persistence schema fingerprinting
- config path defaults
- artifact registration
- generic cleanup dispatch
- restore-state enum conversion

What the concrete element still owns:

- rare custom snapshot preparation when a field must be transformed before persistence
- rare owner-specific restore extensions when the generic declarative model is not enough
- the artifact list it registers in owner-specific cases
- whether an artifact should be reused or rebuilt
- how live runtime handles are recreated after restore or startup

This is the core framework rule: policy is centralized high in the hierarchy, semantics remain local to the owner.

### Declarative Persistence Roles

The current code now prefers declarative field roles over ad hoc `snapshot_state()` implementations.

The main roles are:

- persisted inline state
- artifact descriptor state
- transient runtime-only state
- runtime handles that must be rebuilt

In code this is expressed through field helpers in `AgentElement`:

- `persisted_field(...)`
- `artifact_descriptor_field(...)`
- `transient_field(...)`
- `runtime_handle_field(...)`

What these mean:

- persisted inline state:
  JSON-serializable logical state that should be written into the element snapshot payload
- artifact descriptor state:
  a path-like or descriptor-like value that should be represented as an `ArtifactRecord`, not as a live Python object
- transient runtime-only state:
  local helper state that should not participate in checkpointing
- runtime handle state:
  non-serializable live objects such as locks, clients, threads, models, stores, sessions, and servers that must be recreated

This is intentionally explicit. The runtime does not try to serialize every attribute automatically and silently skip the ones that fail. That would be easier to write initially but much less safe to restore correctly.

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

## Runtime Handle Reconstruction

Runtime handles are now treated as a first-class lifecycle concern rather than an accidental omission from checkpoint payloads.

### Why Runtime Handles Are Excluded

The framework does not checkpoint live objects like:

- `threading.Event`
- `threading.Lock`
- `threading.Thread`
- uvicorn server instances
- LangChain runnable pipelines
- LLM provider client objects
- Chroma/vector-store client objects
- loaded embedding model wrappers
- live data-model method tables and interpreter-bound objects

Those objects are either not serializable or would be incorrect to restore as raw process memory snapshots.

### Reconstruction Rule

The reconstruction rule is now:

1. install the element
2. restore inline persisted fields
3. restore artifact descriptor fields
4. load or reopen owner-managed artifacts
5. rebuild runtime handles
6. validate the restored state

This rule is shared in `AgentElement.restore_from_snapshot(...)`.

### Audited Important Classes

The runtime-handle audit now explicitly covers:

- `Service`
- `ObserverService`
- `RestService`
- `Adapter`
- `LLMService`
- `RAGService`
- `FileEmbeddingService`
- `DataModelService`
- `LearningNode`

For these classes, the code now separates:

- what is checkpointed
- what is represented as an artifact descriptor
- what must be recreated from config or restored descriptors

This matters because a skipped runtime handle is only safe if startup or restore rebuilds it reliably.

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

### Startup Auto-Resume In `Agent.release(...)`

Normal restart behavior now lives in `Agent.release(...)`, not in user scripts.

Current startup flow:

1. finalize deterministic runtime identities for the agent and its elements
2. ensure runtime storage layout exists
3. persist the current config to `config/agent.json`
4. install all current elements
5. load the current checkpoint pointer if one exists
6. compare the current definition against the checkpointed definition
7. restore only exact-match elements
8. fresh-start any changed or newly added elements
9. ignore removed checkpoint elements during restore
10. connect adapters
11. start services
12. enter `RUNNING`

The default resume mode is `EXACT_MATCH_ONLY`.

Exact match means:

- same `uid`
- same class/type
- same definition fingerprint
- same owner scope
- same topology fingerprint for nodes

This is intentionally strict. If an element changed in any way that affects its identity or definition, Stage 1 does not try to migrate it. The changed element is rebuilt and started fresh.

Important current behavior for statemachine services:

- node matching currently depends not only on the node itself, but also on the owning service definition
- because of that, changing one node inside a statemachine service can cause the service and other owned nodes to fresh-start as well
- this is conservative by design in Stage 1
- the current system prefers a safe fresh start over a risky partial restore inside a changed workflow definition

### Reconciliation Outcomes

The current reconciliation report uses three outcomes only:

- `RESTORE_EXACT_MATCH`
- `FRESH_START_CHANGED`
- `REMOVED_IGNORED`

This is a deliberate simplification. The framework does not yet try to interpret whether a change is "compatible enough" to restore. Any change means a fresh start for that element.

Examples:

- same buffer id and same config: restored
- same service id but changed config field: fresh-started
- node moved to a different statemachine service: fresh-started
- node parent or child topology changed: fresh-started
- element removed from the current agent but present in the old checkpoint: ignored during restore

### Manual Restore Flow In `Agent.restore(...)`

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

`Agent.restore(...)` remains available for explicit control and tests. It is not the primary day-to-day restart path anymore. The normal path is automatic reconciliation during `Agent.release(...)`.

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

## Automatic Checkpointing

Automatic checkpointing is now coordinated by `Agent`, not by individual elements.

### Current Trigger Model

The Stage 1 implementation supports:

- explicit manual checkpoint calls
- checkpoint on graceful terminate
- checkpoint on reload
- periodic timer-based checkpoints
- optional checkpoint on quiesce

The runtime stores the checkpoint reason in metadata and manifests. Current reasons are:

- `MANUAL`
- `AUTO_TIMER`
- `TERMINATE`
- `RELOAD`
- `QUIESCE`

### Trigger-Based Behavior

Timer-based checkpoints are now trigger-driven only.

This means the timer loop no longer tries to decide whether enough runtime state changed. If the configured checkpoint condition is met, the runtime creates a checkpoint.

For the current Stage 1 design this is intentional:

- the runtime is long-lived
- periodic snapshots are acceptable even when state changes are small
- checkpoint behavior is easier to reason about when it depends only on explicit triggers

If change-sensitive checkpointing is ever needed later, it should be reintroduced as a separate design step rather than hidden inside the current runtime behavior.

### Checkpoint Scheduler Safeguards

The automatic checkpoint loop is conservative:

- the loop runs in a dedicated agent-owned background thread
- the loop respects a minimum spacing between checkpoints
- the loop skips while the runtime is already checkpointing, restoring, or stopping
- agent-level locks serialize `release()`, `checkpoint()`, `restore()`, `reload_current()`, and `terminate()`

This prevents checkpoint overlap between manual calls, REST calls, and timer-triggered checkpoints.

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

### `AgentElement`

`AgentElement` is now the declarative persistence engine for the whole hierarchy.

It is responsible for:

- interpreting field roles
- building inline payloads from `persisted_field(...)`
- turning `artifact_descriptor_field(...)` values into `ArtifactRecord`s
- excluding transient and runtime-handle fields from payloads
- fingerprinting the persistence schema
- coordinating restore order, including runtime-handle rebuild

For normal element authoring, this is now the most important base class to understand.

### `Buffer`

`Buffer` now declares most of its useful state directly through inherited field roles.

By default it persists:

- the logical buffer contents
- last access timestamps
- timer metadata

By default it treats as runtime-only:

- duplicate buffer references
- lock objects

Concrete buffers should normally only add or refine field roles if they introduce additional runtime state, for example an extra index counter.

`DictBuffer` is a good example of the intended pattern. It inherits the general buffer defaults and only adds its own persisted index counter.

### `Adapter`

`Adapter` now provides the persistence default for adapter-level durable metadata.

By default it persists:

- side-effect receipt records

By default it treats as runtime handles:

- live connections
- sockets
- client objects
- transport/session handles

This is groundwork for safer recovery later. It is not yet a full idempotency system, but it establishes the correct contract split.

### `Service`

`Service` now carries the shared service-level persistence defaults.

By default it persists:

- heartbeat timestamp
- logical pause state
- logical quiesce state
- logical stop state

By default it treats as runtime handles:

- pause/quiesce/stop `Event` objects
- agent references
- threads and external server/client handles introduced by concrete services

This matters because service control state is now restartable without pretending that a live thread or server instance can be serialized directly.

### `Node`

`Node` now persists execution metadata by default:

- activation status
- last execution timestamp
- current execution id
- last transition timestamp
- retry marker
- interrupted flag

`Node.record_output_artifact(...)` lets nodes register generated files as tracked artifacts or side effects without implying that they are fully managed checkpoint payloads.

`Node` also contributes topology metadata to exact-match startup resume. Parent and child relationships are fingerprinted. If a node is rewired between runs, the runtime treats that as a changed definition and fresh-starts the node instead of restoring old execution state into a new workflow topology.

### `LearningNode`

`LearningNode` extends the node defaults with model-oriented state.

By default it persists:

- whether the node still requires learning
- model descriptors produced before checkpoint

By default it treats as runtime handles:

- loaded model objects
- model pipelines
- trainer/runtime session objects

This intentionally avoids trying to serialize live model objects. The base class persists descriptors and provides a rebuild hook, but concrete learning subclasses still need owner-specific logic when they want to turn descriptors back into real runtime models.

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

In simpler terms:

- the framework tells you where an artifact may live and how it is tracked
- the owner tells the framework whether that artifact is valid and how to open or rebuild it

### Concrete Examples In The Current Repo

`RAGService`:

- resolves its own vector-store directory through `_resolve_vector_store_directory()`
- uses `resources/embeddings/...` for its durable vector-store directories
- keeps existing explicit path semantics when configured directly
- uses `resources/models/...` for downloaded embedding-model caches
- registers the resolved vector store as a durable artifact

`FileEmbeddingService`:

- resolves its embedding-store directory itself
- uses `resources/embeddings/...` for durable embedding stores
- uses `resources/models/...` for downloaded embedding-model caches
- registers the embedding store as a durable artifact

`DataModelService`:

- snapshots model instance values into plain dictionaries
- recreates locks and model instances from restored payloads
- reloads model methods from source on install
- intentionally does not try to serialize Python execution state or live locks

`LLMService`:

- persists serializable session-history payloads
- rebuilds `_llm` and `_langchain` runtime handles from config
- recreates in-memory message histories from serialized message payloads

`RestService`:

- treats the FastAPI app, uvicorn server, and service thread as runtime handles
- recreates the app/router setup during install or runtime-handle rebuild
- only starts the live server thread during service start

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

## Runtime Status And Reporting

`Agent.status()` now reports more than simple lifecycle state. It also exposes runtime persistence decisions that are useful for operators and automated tooling.

Current status fields include:

- current lifecycle state
- current `run_id`
- `resume_mode`
- auto-checkpoint configuration
- last checkpoint reason
- last checkpoint success or failure
- last checkpoint error message, if any
- last reconciliation report from startup

The reconciliation report records:

- which checkpoint was used
- which elements were restored exactly
- which elements were fresh-started because they changed
- which old checkpoint elements were ignored because they no longer exist in the current definition

This is especially useful when a restart did not restore everything. The runtime can explain that behavior instead of silently starting cold.

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
- changed elements are not migrated; they are rebuilt and fresh-started
- node ownership or topology changes count as definition changes during auto-resume

## Operational Implications

When extending the repo, keep these operational rules in mind.

### How To Build A New Element

When implementing a new element, follow these checks in order. This checklist is intentionally high-level. It explains what you must think through, not which exact methods every subclass must override.

1. Start from the nearest base class.
   Check `AgentElement`, then the closest family base such as `Buffer`, `Service`, `Adapter`, `Node`, or `LearningNode`.
   Confirm which lifecycle and persistence behavior is already covered there before adding custom code.

2. Classify the element state.
   Decide which values are:
   - inline persisted state
   - artifact-backed descriptor state
   - transient runtime-only helpers
   - runtime handles that must be rebuilt

3. Declare the field roles.
   Prefer field helpers and inherited family defaults over custom snapshot methods.
   Only deviate when a field genuinely needs custom transformation or custom rebuild behavior.

4. Check non-checkpointed runtime handles explicitly.
   If the element owns models, DB clients, vector stores, threads, sessions, locks, servers, or external SDK handles, make sure startup and restore rebuild them correctly.
   A skipped handle is only safe if there is a reliable reconstruction path.

5. Verify owner-local artifact behavior.
   If the element owns files, local DBs, vector stores, caches, or output directories, confirm whether startup should:
   - reuse them
   - reopen them
   - validate them
   - rebuild them
   Also decide whether they belong to:
   - the agent runtime under `resources/runtime/<agent_uid>/...`
   - or a shared top-level resource root such as `resources/models/...`, `resources/embeddings/...`, `resources/inputs/...`, or `resources/outputs/...`

6. Check exact-match behavior.
   If parent ownership, node topology, or config changes should invalidate restore, make sure the current definition fingerprint reflects that correctly.
   Be conservative. When you are unsure whether old state is still safe in a new definition, prefer a fresh start.

7. Write focused tests.
   At minimum test:
   - checkpoint round-trip of the logical state
   - startup or restore reconstruction of runtime handles
   - fresh-start behavior when the definition changes
   - artifact reuse or rebuild behavior when relevant

This is the intended authoring model: use inherited defaults first, add the smallest amount of owner-specific persistence logic necessary, and test the restart path explicitly.

### A Simple Mental Model

If you only remember four rules from this document, remember these:

1. `Agent` decides when checkpointing and restore happen.
2. `AgentElement` decides how one element is turned into a snapshot and restored again.
3. Shared base classes such as `Buffer`, `Service`, `Adapter`, `Node`, and `LearningNode` should carry most of the common logic.
4. Concrete elements still own the meaning of their artifacts, models, databases, stores, and other runtime handles.

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
