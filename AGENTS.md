# Repository guidance for coding agents

## Purpose

Generate maintainable code that fits PyDataAgents, a Python 3.11+ framework for industrial data collection, automation, and data processing. Implement the requested behavior completely while keeping changes focused.

## Before writing code

- Read `README.md`, `Contribute.md`, and `pyproject.toml` for architecture, contribution rules, and dependencies.
- Inspect the relevant base classes, a nearby implementation, and its tests before adding a component. Use actual source signatures rather than guessing APIs.
- Check the working tree and preserve existing user changes.
- Reuse existing components and utilities. Avoid unrelated refactoring, formatting changes, and speculative abstractions.
- Resolve routine implementation choices using repository conventions. Ask for clarification when missing requirements materially affect behavior or compatibility.
- existing components are described in the following doc files: 
  - `pydag/_docs/Agents.md`: agent composition, configuration, lifecycle, applications, and interfaces.
  - `pydag/_docs/Buffers.md`: data storage, signals, geometry, and buffer transformations.
  - `pydag/_docs/Services.md`: reusable runtime capabilities, integrations, and background services
  - `pydag/_docs/Actions and Transitions.md`: workflow actions, transitions, and processing steps

## Where code belongs

- `pydag/agents/`: agent composition, configuration, lifecycle, applications, and interfaces.
- `pydag/buffers/`: data storage, signals, geometry, and buffer transformations.
- `pydag/services/`: reusable runtime capabilities, integrations, and background services, grouped by domain.
- `pydag/nodes/`: workflow actions, transitions, and processing steps, grouped by domain.
- `pydag/utils/`: shared helpers that do not belong to a specific component.
- `tests/unit/`: focused tests, following the corresponding source directory structure.
- `tests/regression/`: regression and integration scenarios.
- `pydag/_docs/`: framework documentation and related assets.

## Framework conventions

- Build on the appropriate existing base class, such as `AgentElement`, `Buffer`, `Service`, `ObserverService`, `MappingService`, `Action`, `BufferNode` and `ServiceNode`.
- Use buffers for data exchange between services and nodes. Reuse existing mapping and state-machine mechanisms where they fit.
- Implement lifecycle hooks expected by the base class. Preserve required superclass initialization and hook behavior, including `super().__post_init__()` when applicable.
- Keep service startup non-blocking. Stop background work and release connections, files, and other resources during shutdown or uninstall as appropriate.
- Keep imports and constructors free of external connections, long-running work, and application startup side effects.
- Follow nearby dataclass configuration patterns. Use `field(default_factory=...)` for mutable defaults and provide field metadata where the configuration interface expects it.
- Keep runtime resources separate from serializable configuration. Preserve public configuration names, element IDs, and fully qualified type paths used by saved configurations.
- Prefer public buffer and component APIs. Inspect ownership and synchronization requirements before accessing private state.

## Python style and dependencies

- Follow the surrounding code's naming and import style. Component modules commonly use the class name, for example `CopyBufferAction.py`.
- Add useful type annotations to new interfaces and concise docstrings explaining behavior, units, configuration, and exceptions where relevant.
- Keep functions cohesive. Validate inputs at boundaries and raise meaningful errors; do not silently swallow failures.
- Use the existing logging approach, typically `loguru`, for runtime diagnostics. Do not log credentials or sensitive payloads.
- Prefer the standard library and existing dependencies. Declare necessary new dependencies in `pyproject.toml`, placing integration-specific packages in the appropriate optional extra.
- Keep optional integrations isolated so unrelated core functionality does not require their packages or platform-specific software.
- Do not introduce a formatter, linter, framework, or broad dependency upgrade solely for a small feature.
- Use portable paths and configurable endpoints. Do not embed machine-specific paths, credentials, or production data.

## Validation

- For new behavior, add focused tests covering the expected result and meaningful edge cases or failure paths. Fixes should include a regression test when practical.
- Prefer deterministic assertions, temporary directories, and mocked external boundaries. Avoid tests that only print results, sleep unnecessarily, or depend on live services.
- Inspect existing tests before executing them: even files under `tests/unit/` may require hardware, network access, credentials, downloads, or a GUI.
- Use the project's existing Python environment. When setup is needed, the base test installation is `python -m pip install -e ".[test]"`; install only the additional extras needed for the task.
- Run focused checks first, for example `python -m pytest tests/unit/utils/test_stringutils.py`. Replace that path with tests relevant to the change.
- The full-suite command is `python -m pytest`. `Contribute.md` requires all tests to pass before opening a PR. If the required environment is unavailable, report the limitation and do not claim full validation or PR readiness.
- For documentation-only changes, check accuracy, paths, and Markdown instead of running unrelated runtime tests.

## Finishing a change

- Update relevant documentation and examples when public behavior or configuration changes. Include a minimal usage example for a new component when useful.
- Review the diff for unintended edits, generated files, secrets, and compatibility changes.
- Follow `Contribute.md` for branches and PRs; never push directly to `develop`. Do not commit, push, or publish unless requested.
- Summarize what changed, the checks actually run, and any remaining limitations. Clearly distinguish completed implementation from unverified integration behavior.
