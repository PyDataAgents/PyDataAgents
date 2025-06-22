# Node Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Action`](#action-from-Action) |  |
| [`AdapterNode`](#adapternode-from-AdapterNode) | AdapterNode is a specialized BufferNode that integrates an adapter for data processing. |
| [`BufferNode`](#buffernode-from-BufferNode) |  |
| [`GrabberNode`](#grabbernode-from-GrabberNode) |  |
| [`JoinTransition`](#jointransition-from-JoinTransition) |  |
| [`MappingNode`](#mappingnode-from-MappingNode) |  |
| [`ServiceNode`](#servicenode-from-ServiceNode) | A class representing a service node in a state machine. |
| [`Transition`](#transition-from-Transition) |  |
| [`AdapterReadAction`](#adapterreadaction-from-actions\AdapterReadAction) | Action to read data from an adapter. |
| [`AdapterWriteAction`](#adapterwriteaction-from-actions\AdapterWriteAction) | Action to write data with an adapter. |
| [`AddBufferAction`](#addbufferaction-from-actions\AddBufferAction) | Action to add a buffer to the grabber node. |
| [`BrowserAutomationAction`](#browserautomationaction-from-actions\BrowserAutomationAction) |  |
| [`ConfigureElementAction`](#configureelementaction-from-actions\ConfigureElementAction) | this `Action` configures a `GrabberElement` property by the provided `element_id` and name of the `option`, which is the class' property |
| [`CopyFilesAction`](#copyfilesaction-from-actions\CopyFilesAction) |  |
| [`ListFilesAction`](#listfilesaction-from-actions\ListFilesAction) |  |
| [`MailAction`](#mailaction-from-actions\MailAction) |  |
| [`MoveFilesAction`](#movefilesaction-from-actions\MoveFilesAction) |  |
| [`ReadCsvAction`](#readcsvaction-from-actions\ReadCsvAction) |  |
| [`ReadJsonAction`](#readjsonaction-from-actions\ReadJsonAction) |  |
| [`SetElementAction`](#setelementaction-from-actions\SetElementAction) |  |
| [`SleepAction`](#sleepaction-from-actions\SleepAction) | An action that sleeps for a specified number of seconds. |
| [`StartAction`](#startaction-from-actions\StartAction) | An action that starts the state machine. |
| [`StopAction`](#stopaction-from-actions\StopAction) | An action that stops the state machine. |
| [`UrlNavigateAction`](#urlnavigateaction-from-actions\UrlNavigateAction) |  |
| [`BufferInRangeTransition`](#bufferinrangetransition-from-transitions\BufferInRangeTransition) | A transition that compares the current buffer with a target value. |
| [`CompareBufferTransition`](#comparebuffertransition-from-transitions\CompareBufferTransition) | A transition that compares the current buffer with a target value. |
| [`FalseTransition`](#falsetransition-from-transitions\FalseTransition) | A transition that always returns False. |
| [`TrueTransition`](#truetransition-from-transitions\TrueTransition) | A transition that always returns True. |



## `Action` (from `Action.py`)

_No fields defined._

## `AdapterNode` (from `AdapterNode.py`)

AdapterNode is a specialized BufferNode that integrates an adapter for data processing.
It inherits from BufferNode to manage buffers and provides methods to interact with the adapter.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `adapter_id` | `str` | `` | ID of the adapter |


```python
# Example usage of `AdapterNode`
from pydatagrabber import AdapterNode  # Adjust import if needed

obj = AdapterNode(
    adapter_id="<string>"
)
```

## `BufferNode` (from `BufferNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `buffer_id` | `str` | `` | unique ID of the buffer |


```python
# Example usage of `BufferNode`
from pydatagrabber import BufferNode  # Adjust import if needed

obj = BufferNode(
    buffer_id="<string>"
)
```

## `GrabberNode` (from `GrabberNode.py`)

_No fields defined._

## `JoinTransition` (from `JoinTransition.py`)

_No fields defined._

## `MappingNode` (from `MappingNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping_id` | `str` | `` | ID of the mapping |


```python
# Example usage of `MappingNode`
from pydatagrabber import MappingNode  # Adjust import if needed

obj = MappingNode(
    mapping_id="<string>"
)
```

## `ServiceNode` (from `ServiceNode.py`)

A class representing a service node in a state machine.
Inherits from Node and adds functionality specific to service nodes.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `service_id` | `str` | `` | ID of the service |


```python
# Example usage of `ServiceNode`
from pydatagrabber import ServiceNode  # Adjust import if needed

obj = ServiceNode(
    service_id="<string>"
)
```

## `Transition` (from `Transition.py`)

_No fields defined._

## `AdapterReadAction` (from `actions\AdapterReadAction.py`)

Action to read data from an adapter.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `address` | `str` | `` | The address to read from the adapter. |
| `n` | `int` | `1` | The number of samples to read. |


```python
# Example usage of `AdapterReadAction`
from pydatagrabber import AdapterReadAction  # Adjust import if needed

obj = AdapterReadAction(
    address="<string>",
    n=1
)
```

## `AdapterWriteAction` (from `actions\AdapterWriteAction.py`)

Action to write data with an adapter.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `address` | `str` | `` | The address to read from the adapter. |
| `n` | `int` | `1` | The number of samples to read. |
| `persistent` | `bool` | `False` | If True, the data will be stored in a persistent buffer. |


```python
# Example usage of `AdapterWriteAction`
from pydatagrabber import AdapterWriteAction  # Adjust import if needed

obj = AdapterWriteAction(
    address="<string>",
    n=1,
    persistent=False
)
```

## `AddBufferAction` (from `actions\AddBufferAction.py`)

Action to add a buffer to the grabber node.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `config` | `dict` | `` | Configuration for the buffer to be added. |


```python
# Example usage of `AddBufferAction`
from pydatagrabber import AddBufferAction  # Adjust import if needed

obj = AddBufferAction(
    config={}
)
```

## `BrowserAutomationAction` (from `actions\BrowserAutomationAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |


```python
# Example usage of `BrowserAutomationAction`
from pydatagrabber import BrowserAutomationAction  # Adjust import if needed

obj = BrowserAutomationAction(
    service_id="<string>"
)
```

## `ConfigureElementAction` (from `actions\ConfigureElementAction.py`)

this `Action` configures a `GrabberElement` property by the provided `element_id` and name of the `option`, which is the class' property
<br>the new property value is derived from the `Node`'s `buffer`

Args:
    GrabberNode (_type_): inherits from class GrabberNode
    BufferNode (_type_): inherits from class BufferNode

Raises:
    StatemachineException: if an error occurs during execute
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `option` | `str` | `` | option to configure with new value |
| `element_id` | `str` | `` | id of the element to change the option for |
| `n` | `int` | `1` | specifies the number of samples to remove from buffer |


```python
# Example usage of `ConfigureElementAction`
from pydatagrabber import ConfigureElementAction  # Adjust import if needed

obj = ConfigureElementAction(
    option="<string>",
    element_id="<string>",
    n=1
)
```

## `CopyFilesAction` (from `actions\CopyFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `target_folder` | `str` | `` | target folder to copy all the files to in Buffer |


```python
# Example usage of `CopyFilesAction`
from pydatagrabber import CopyFilesAction  # Adjust import if needed

obj = CopyFilesAction(
    target_folder="path/to/folder"
)
```

## `ListFilesAction` (from `actions\ListFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `folder` | `str` | `` | folder to list the files from into a Buffer |
| `pattern` | `str` | `` | paatern to look for in file names |
| `extension` | `str` | `` | extension to include |
| `newer_than_seconds` | `int` | `` | specifies how old in seconds a file can be to be included |


```python
# Example usage of `ListFilesAction`
from pydatagrabber import ListFilesAction  # Adjust import if needed

obj = ListFilesAction(
    folder="path/to/folder",
    pattern="<string>",
    extension="<string>",
    newer_than_seconds=1
)
```

## `MailAction` (from `actions\MailAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `smtp_server` | `str` | `` | host of the mail server to use |
| `port` | `int` | `` | port of the smtp server |
| `mail_account` | `str` | `` | mail account to use for login |
| `pw` | `str` | `` | password of the mail server |
| `recipient` | `str` | `` | mail address of the recipient |
| `subject` | `str` | `` | subject of the mail |
| `body` | `str` | `` | body of the mail |


```python
# Example usage of `MailAction`
from pydatagrabber import MailAction  # Adjust import if needed

obj = MailAction(
    smtp_server="<string>",
    port=1,
    mail_account="<string>",
    pw="<string>",
    recipient="<string>",
    subject="<string>",
    body="<string>"
)
```

## `MoveFilesAction` (from `actions\MoveFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `target_folder` | `str` | `` | target folder to move all the files to in Buffer |


```python
# Example usage of `MoveFilesAction`
from pydatagrabber import MoveFilesAction  # Adjust import if needed

obj = MoveFilesAction(
    target_folder="path/to/folder"
)
```

## `ReadCsvAction` (from `actions\ReadCsvAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `file_path` | `str` | `` | path to the csv file to read the data from |
| `delimiter` | `str` | `';'` | delimiter character(s) for this csv file |


```python
# Example usage of `ReadCsvAction`
from pydatagrabber import ReadCsvAction  # Adjust import if needed

obj = ReadCsvAction(
    file_path="path/to/file.txt",
    delimiter=';'
)
```

## `ReadJsonAction` (from `actions\ReadJsonAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `file_path` | `str` | `` | path to the json file to read the data from |
| `json_path` | `str` | `` | path to the json file to read the data from |


```python
# Example usage of `ReadJsonAction`
from pydatagrabber import ReadJsonAction  # Adjust import if needed

obj = ReadJsonAction(
    file_path="path/to/file.txt",
    json_path="<string>"
)
```

## `SetElementAction` (from `actions\SetElementAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `xpath` | `str` | `` | XPath definition to locate the element to set a value to |


```python
# Example usage of `SetElementAction`
from pydatagrabber import SetElementAction  # Adjust import if needed

obj = SetElementAction(
    xpath="<string>"
)
```

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

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | `str` | `` | url to navigate to in browser |


```python
# Example usage of `UrlNavigateAction`
from pydatagrabber import UrlNavigateAction  # Adjust import if needed

obj = UrlNavigateAction(
    url="https://example.com"
)
```

## `BufferInRangeTransition` (from `transitions\BufferInRangeTransition.py`)

A transition that compares the current buffer with a target value.
If the buffer matches the target, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `comparator` | `str` | `` | The comparison operator to use. |
| `value` | `any` | `` | The value to compare against the buffer. |


```python
# Example usage of `BufferInRangeTransition`
from pydatagrabber import BufferInRangeTransition  # Adjust import if needed

obj = BufferInRangeTransition(
    comparator="<string>",
    value="<value>"
)
```

## `CompareBufferTransition` (from `transitions\CompareBufferTransition.py`)

A transition that compares the current buffer with a target value.
If the buffer matches the target, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `comparator` | `str` | `` | The comparison operator to use. |
| `value` | `any` | `` | The value to compare against the buffer. |


```python
# Example usage of `CompareBufferTransition`
from pydatagrabber import CompareBufferTransition  # Adjust import if needed

obj = CompareBufferTransition(
    comparator="<string>",
    value="<value>"
)
```

## `FalseTransition` (from `transitions\FalseTransition.py`)

A transition that always returns False.
_No fields defined._

## `TrueTransition` (from `transitions\TrueTransition.py`)

A transition that always returns True.
This is used to test the statemachine without any conditions.
_No fields defined._
