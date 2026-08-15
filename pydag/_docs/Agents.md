# Agents Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Agent`](#agent-in-pydagagentsagentpy) | `Agent` class for managing a multi-component application system.The `Agent` serves as the central orchestrator for managing Buffers, Nodes and Services.It handles the lifecycle of these components including installation, initialization, connection,and termination. The `Agent` supports optional features such as persistence, REST API exposure,and configurable startup behavior.Args:    id (str): Unique identifier for the `Agent` application. Auto-generated if not provided.    load_on_install (bool): If True, all `AgentElements` are set to load_on_install=True. Defaults to False.    with_persistence (bool): If True, an `AgentPersistService` is created by default to continuously        save `AgentElements` to local files. Defaults to False.    description (str): Application/agent description. Defaults to None.    buffer_store (dict[str, Buffer]): Dictionary storing all `Buffer` instances in the `Agent`.    service_store (dict[str, Service]): Dictionary storing all `Service` instances in the `Agent`.        to install or uninstall.Raises:    AgentException: _description_    AgentException: _description_Returns:    _type_: _description_ |
| [`AgentElement`](#agentelement-in-pydagagentsagentelementpy) | Abstract base class for agent elements. |
| [`AgentApp`](#agentapp-in-pydagagentsappagentapppy) | Application that stores an `Agent` and provides REST API and UI based on configuration settings  |
| [`AgentStoreApp`](#agentstoreapp-in-pydagagentsappagentstoreapppy) | Application that stores an `AgentStore` and provides a REST API and UI based on configuration settings  |



## `Agent` (in `pydag\agents\Agent.py`)

`Agent` class for managing a multi-component application system.
The `Agent` serves as the central orchestrator for managing Buffers, Nodes and Services.
It handles the lifecycle of these components including installation, initialization, connection,
and termination. The `Agent` supports optional features such as persistence, REST API exposure,
and configurable startup behavior.

Args:
    id (str): Unique identifier for the `Agent` application. Auto-generated if not provided.
    load_on_install (bool): If True, all `AgentElements` are set to load_on_install=True. Defaults to False.
    with_persistence (bool): If True, an `AgentPersistService` is created by default to continuously
        save `AgentElements` to local files. Defaults to False.
    description (str): Application/agent description. Defaults to None.
    buffer_store (dict[str, Buffer]): Dictionary storing all `Buffer` instances in the `Agent`.
    service_store (dict[str, Service]): Dictionary storing all `Service` instances in the `Agent`.
        to install or uninstall.
Raises:
    AgentException: _description_
    AgentException: _description_

Returns:
    _type_: _description_
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `id` | `str` | `'lambda: str(uuid.uuid4())()'` | unique identifier of Agent |
| `description` | `str` | `"<string>"` | application/agent description |
| `load_on_install` | `bool` | `False` | if True, all AgentElements are set to load_on_install = True |
| `with_persistence` | `bool` | `False` | if True, an AgentPersistService is created by default to contuinously save the AgentElements in a local files |
| `save_folder` | `str` | `'AgentKeywords.SAVE_FOLDER'` | folder to save the AgentElements in local files, if None, a default folder is created in the current working directory |
| `buffer_store` | `dict[str, Buffer]` | `'dict()'` | dictionary of Buffers in the Agent |
| `service_store` | `dict[str, Service]` | `'dict()'` | dictionary of Services in the Agent |


```python
# Example usage of `Agent`
from pydag.agents.Agent import Agent  # Adjust import if needed

agent = Agent(
	id="<string>",
	load_on_install=False,
	id='lambda: str(uuid.uuid4())()',
	description="<string>",
	load_on_install=False,
	with_persistence=False,
	save_folder='AgentKeywords.SAVE_FOLDER',
	buffer_store='dict()',
	service_store='dict()'
)
```

[Go to Summary](#summary)
## `AgentElement` (in `pydag\agents\AgentElement.py`)

Abstract base class for agent elements.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `type` | `str` | `"<string>"` | fully qualified package and class name descriptor |
| `id` | `str` | `'lambda: str(uuid.uuid4())()'` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `AgentElement`
from pydag.agents.AgentElement import AgentElement  # Adjust import if needed

agent_element = AgentElement(
	id="<string>",
	load_on_install=False,
	type="<string>",
	id='lambda: str(uuid.uuid4())()',
	load_on_install=False
)
```

[Go to Summary](#summary)
## `AgentApp` (in `pydag\agents\app\AgentApp.py`)

Application that stores an `Agent` and provides REST API and UI based on configuration settings 
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `host` | `str` | `'localhost'` |  |
| `port` | `int` | `8081` | port for the REST API Service |
| `with_api` | `bool` | `False` | if True, a REST API Service is created by default for REST interactions on port specified in port |
| `api_key_file` | `str` | `"path/to/file.txt"` | file path for API key storage and loading |
| `with_ui` | `bool` | `False` | if True, a NiceGUI UI is created by default for the Agent |
| `dark_mode` | `bool` | `True` | enables dark mode |
| `color_schema` | `dict` | `'dict()'` | color schema for the ui, see https://nicegui.io/docs/colors for more details |
| `with_config` | `bool` | `False` |  |
| `agent` | `Agent` | `'Agent()'` | the `Agent` instance to be used by the `AgentApp` |
| `ui_pages` | `list[UIPage]` | `'list()'` | list of UIPage instances to be used by the `AgentApp` |


```python
# Example usage of `AgentApp`
from pydag.agents.app.AgentApp import AgentApp  # Adjust import if needed

agent_app = AgentApp(
	id="<string>",
	load_on_install=False,
	host='localhost',
	port=8081,
	with_api=False,
	api_key_file="path/to/file.txt",
	with_ui=False,
	dark_mode=True,
	color_schema='dict()',
	with_config=False,
	agent='Agent()',
	ui_pages='list()'
)
```

[Go to Summary](#summary)
## `AgentStoreApp` (in `pydag\agents\app\AgentStoreApp.py`)

Application that stores an `AgentStore` and provides a REST API and UI based on configuration settings 
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `host` | `str` | `'localhost'` |  |
| `port` | `int` | `8081` | port for the REST API Service |
| `with_api` | `bool` | `False` | if True, a REST API Service is created by default for REST interactions on port specified in port |
| `api_key_file` | `str` | `"path/to/file.txt"` | file path for API key storage and loading |
| `dark_mode` | `bool` | `True` | enables dark mode |
| `color_schema` | `dict` | `'dict()'` | color schema for the ui, see https://nicegui.io/docs/colors for more details |
| `with_config` | `bool` | `False` |  |
| `agent` | `Agent` | `'Agent()'` | the `Agent` instance to be used by the `AgentApp` |
| `ui_pages` | `list[UIPage]` | `'list()'` | list of UIPage instances to be used by the `AgentApp` |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `with_ui` | `bool` | `True` | Whether to create a UI for the agent store |


```python
# Example usage of `AgentStoreApp`
from pydag.agents.app.AgentStoreApp import AgentStoreApp  # Adjust import if needed

agent_store_app = AgentStoreApp(
	host='localhost',
	port=8081,
	with_api=False,
	api_key_file="path/to/file.txt",
	dark_mode=True,
	color_schema='dict()',
	with_config=False,
	agent='Agent()',
	ui_pages='list()',
	id="<string>",
	load_on_install=False,
	with_ui=True
)
```

[Go to Summary](#summary)