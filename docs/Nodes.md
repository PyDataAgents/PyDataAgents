# + Node Documentation

## `Action` (from `Action.py`)

_No fields defined._

## `AdapterNode` (from `AdapterNode.py`)

AdapterNode is a specialized BufferNode that integrates an adapter for data processing.
It inherits from BufferNode to manage buffers and provides methods to interact with the adapter.
| Field | Type | Description |
|-------|------|-------------|
| `adapter_id` | `str` | ID of the adapter |

## `BufferNode` (from `BufferNode.py`)

| Field | Type | Description |
|-------|------|-------------|
| `buffer_id` | `str` | unique ID of the buffer |

## `GrabberNode` (from `GrabberNode.py`)

_No fields defined._

## `JoinTransition` (from `JoinTransition.py`)

_No fields defined._

## `MappingNode` (from `MappingNode.py`)

| Field | Type | Description |
|-------|------|-------------|
| `mapping_id` | `str` | ID of the mapping |

## `ServiceNode` (from `ServiceNode.py`)

A class representing a service node in a state machine.
Inherits from Node and adds functionality specific to service nodes.
| Field | Type | Description |
|-------|------|-------------|
| `service_id` | `str` | ID of the service |

## `Transition` (from `Transition.py`)

_No fields defined._

## `AdapterReadAction` (from `actions\AdapterReadAction.py`)

Action to read data from an adapter.
| Field | Type | Description |
|-------|------|-------------|
| `address` | `str` | The address to read from the adapter. |
| `n` | `int` | The number of samples to read. |

## `AdapterWriteAction` (from `actions\AdapterWriteAction.py`)

Action to write data with an adapter.
| Field | Type | Description |
|-------|------|-------------|
| `address` | `str` | The address to read from the adapter. |
| `n` | `int` | The number of samples to read. |
| `persistent` | `bool` | If True, the data will be stored in a persistent buffer. |

## `AddBufferAction` (from `actions\AddBufferAction.py`)

Action to add a buffer to the grabber node.
| Field | Type | Description |
|-------|------|-------------|
| `config` | `dict` | Configuration for the buffer to be added. |

## `BrowserAutomationAction` (from `actions\BrowserAutomationAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `service_id` | `str` | ID of the service to reference for Browser Automation |

## `ConfigureElementAction` (from `actions\ConfigureElementAction.py`)

this `Action` configures a `GrabberElement` property by the provided `element_id` and name of the `option`, which is the class' property
<br>the new property value is derived from the `Node`'s `buffer`

Args:
    GrabberNode (_type_): inherits from class GrabberNode
    BufferNode (_type_): inherits from class BufferNode

Raises:
    StatemachineException: if an error occurs during execute
| Field | Type | Description |
|-------|------|-------------|
| `option` | `str` | option to configure with new value |
| `element_id` | `str` | id of the element to change the option for |
| `n` | `int` | specifies the number of samples to remove from buffer |

## `CopyFilesAction` (from `actions\CopyFilesAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `target_folder` | `str` | target folder to copy all the files to in Buffer |

## `ListFilesAction` (from `actions\ListFilesAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `folder` | `str` | folder to list the files from into a Buffer |
| `pattern` | `str` | paatern to look for in file names |
| `extension` | `str` | extension to include |
| `newer_than_seconds` | `int` | specifies how old in seconds a file can be to be included |

## `MailAction` (from `actions\MailAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `smtp_server` | `str` | host of the mail server to use |
| `port` | `int` | port of the smtp server |
| `mail_account` | `str` | mail account to use for login |
| `pw` | `str` | password of the mail server |
| `recipient` | `str` | mail address of the recipient |
| `subject` | `str` | subject of the mail |
| `body` | `str` | body of the mail |

## `MoveFilesAction` (from `actions\MoveFilesAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `target_folder` | `str` | target folder to move all the files to in Buffer |

## `ReadCsvAction` (from `actions\ReadCsvAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | path to the csv file to read the data from |
| `delimiter` | `str` | delimiter character(s) for this csv file |

## `ReadJsonAction` (from `actions\ReadJsonAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | path to the json file to read the data from |
| `json_path` | `str` |  |

## `SetElementAction` (from `actions\SetElementAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `xpath` | `str` | XPath definition to locate the element to set a value to |

## `SleepAction` (from `actions\SleepAction.py`)

An action that sleeps for a specified number of seconds.
_No fields defined._

## `StartAction` (from `actions\StartAction.py`)

An action that starts the state machine.
_No fields defined._

## `StopAction` (from `actions\StopAction.py`)

An action that stops the state machine.
_No fields defined._

## `UrlNavigateAction` (from `actions\UrlNavigateAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `url` | `str` | url to navigate to in browser |

## `BufferInRangeTransition` (from `transitions\BufferInRangeTransition.py`)

A transition that compares the current buffer with a target value.
If the buffer matches the target, the transition is successful.
| Field | Type | Description |
|-------|------|-------------|
| `comparator` | `str` | The comparison operator to use. |
| `value` | `any` | The value to compare against the buffer. |

## `CompareBufferTransition` (from `transitions\CompareBufferTransition.py`)

A transition that compares the current buffer with a target value.
If the buffer matches the target, the transition is successful.
| Field | Type | Description |
|-------|------|-------------|
| `comparator` | `str` | The comparison operator to use. |
| `value` | `any` | The value to compare against the buffer. |

## `FalseTransition` (from `transitions\FalseTransition.py`)

A transition that always returns False.
_No fields defined._

## `TrueTransition` (from `transitions\TrueTransition.py`)

A transition that always returns True.
This is used to test the statemachine without any conditions.
_No fields defined._
