# Actions and Transitions Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Action`](#action-from-Action) |  |
| [`AdapterNode`](#adapternode-from-AdapterNode) | AdapterNode is a specialized BufferNode that integrates an adapter for data processing.It inherits from BufferNode to manage buffers and provides methods to interact with the adapter. |
| [`BufferNode`](#buffernode-from-BufferNode) |  |
| [`GrabberNode`](#grabbernode-from-GrabberNode) |  |
| [`JoinTransition`](#jointransition-from-JoinTransition) |  |
| [`MappingNode`](#mappingnode-from-MappingNode) |  |
| [`Node`](#node-from-Node) |  |
| [`ServiceNode`](#servicenode-from-ServiceNode) | A class representing a service node in a state machine.Inherits from Node and adds functionality specific to service nodes. |
| [`Transition`](#transition-from-Transition) |  |
| [`AdapterReadAction`](#adapterreadaction-from-actions\AdapterReadAction) | Action to read data from an adapter. |
| [`AdapterWriteAction`](#adapterwriteaction-from-actions\AdapterWriteAction) | Action to write data with an adapter. |
| [`AddBufferAction`](#addbufferaction-from-actions\AddBufferAction) | Action to add a buffer to the grabber node. |
| [`BrowserAutomationAction`](#browserautomationaction-from-actions\BrowserAutomationAction) |  |
| [`ConfigureElementAction`](#configureelementaction-from-actions\ConfigureElementAction) | this `Action` configures a `GrabberElement` property by the provided `element_id` and name of the `option`, which is the class' property<br>the new property value is derived from the `Node`'s `buffer`Args:    GrabberNode (_type_): inherits from class GrabberNode    BufferNode (_type_): inherits from class BufferNodeRaises:    StatemachineException: if an error occurs during execute |
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
| [`BufferInRangeTransition`](#bufferinrangetransition-from-transitions\BufferInRangeTransition) | A transition that compares the current buffer with a target value.If the buffer matches the target, the transition is successful. |
| [`CompareBufferTransition`](#comparebuffertransition-from-transitions\CompareBufferTransition) | A transition that compares the current buffer with a target value.If the buffer matches the target, the transition is successful. |
| [`FalseTransition`](#falsetransition-from-transitions\FalseTransition) | A transition that always returns False. |
| [`TrueTransition`](#truetransition-from-transitions\TrueTransition) | A transition that always returns True.This is used to test the statemachine without any conditions. |



## `Action` (from `Action.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Action`
from pydatagrabber import Action  # Adjust import if needed

obj = Action()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `AdapterNode` (from `AdapterNode.py`)

AdapterNode is a specialized BufferNode that integrates an adapter for data processing.
It inherits from BufferNode to manage buffers and provides methods to interact with the adapter.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `adapter_id` | `str` | `` | ID of the adapter |


```python
# Example usage of `AdapterNode`
from pydatagrabber import AdapterNode  # Adjust import if needed

obj = AdapterNode()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.adapter_id="<string>"
```

## `BufferNode` (from `BufferNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `buffer_id` | `str` | `` | unique ID of the buffer |


```python
# Example usage of `BufferNode`
from pydatagrabber import BufferNode  # Adjust import if needed

obj = BufferNode()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
obj.buffer_id="<string>"
```

## `GrabberNode` (from `GrabberNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `GrabberNode`
from pydatagrabber import GrabberNode  # Adjust import if needed

obj = GrabberNode()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `JoinTransition` (from `JoinTransition.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `JoinTransition`
from pydatagrabber import JoinTransition  # Adjust import if needed

obj = JoinTransition()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `MappingNode` (from `MappingNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `mapping_id` | `str` | `` | ID of the mapping |


```python
# Example usage of `MappingNode`
from pydatagrabber import MappingNode  # Adjust import if needed

obj = MappingNode()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
obj.mapping_id="<string>"
```

## `Node` (from `Node.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |


```python
# Example usage of `Node`
from pydatagrabber import Node  # Adjust import if needed

obj = Node()
obj.id="<string>"
obj.load_on_install=False
obj.child_ids='list()()'
```

## `ServiceNode` (from `ServiceNode.py`)

A class representing a service node in a state machine.
Inherits from Node and adds functionality specific to service nodes.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `service_id` | `str` | `` | ID of the service |


```python
# Example usage of `ServiceNode`
from pydatagrabber import ServiceNode  # Adjust import if needed

obj = ServiceNode()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
obj.service_id="<string>"
```

## `Transition` (from `Transition.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Transition`
from pydatagrabber import Transition  # Adjust import if needed

obj = Transition()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `AdapterReadAction` (from `actions\AdapterReadAction.py`)

Action to read data from an adapter.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `adapter_id` | `str` | `` | ID of the adapter |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `address` | `str` | `` | The address to read from the adapter. |
| `n` | `int` | `1` | The number of samples to read. |


```python
# Example usage of `AdapterReadAction`
from pydatagrabber import AdapterReadAction  # Adjust import if needed

obj = AdapterReadAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.adapter_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.address="<string>"
obj.n=1
```

## `AdapterWriteAction` (from `actions\AdapterWriteAction.py`)

Action to write data with an adapter.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `adapter_id` | `str` | `` | ID of the adapter |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `address` | `str` | `` | The address to read from the adapter. |
| `n` | `int` | `1` | The number of samples to read. |
| `persistent` | `bool` | `False` | If True, the data will be stored in a persistent buffer. |


```python
# Example usage of `AdapterWriteAction`
from pydatagrabber import AdapterWriteAction  # Adjust import if needed

obj = AdapterWriteAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.adapter_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.address="<string>"
obj.n=1
obj.persistent=False
```

## `AddBufferAction` (from `actions\AddBufferAction.py`)

Action to add a buffer to the grabber node.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `config` | `dict` | `` | Configuration for the buffer to be added. |


```python
# Example usage of `AddBufferAction`
from pydatagrabber import AddBufferAction  # Adjust import if needed

obj = AddBufferAction()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
obj.config={}
```

## `BrowserAutomationAction` (from `actions\BrowserAutomationAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |


```python
# Example usage of `BrowserAutomationAction`
from pydatagrabber import BrowserAutomationAction  # Adjust import if needed

obj = BrowserAutomationAction()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
obj.service_id="<string>"
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
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `option` | `str` | `` | option to configure with new value |
| `element_id` | `str` | `` | id of the element to change the option for |
| `n` | `int` | `1` | specifies the number of samples to remove from buffer |


```python
# Example usage of `ConfigureElementAction`
from pydatagrabber import ConfigureElementAction  # Adjust import if needed

obj = ConfigureElementAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.option="<string>"
obj.element_id="<string>"
obj.n=1
```

## `CopyFilesAction` (from `actions\CopyFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `target_folder` | `str` | `` | target folder to copy all the files to in Buffer |


```python
# Example usage of `CopyFilesAction`
from pydatagrabber import CopyFilesAction  # Adjust import if needed

obj = CopyFilesAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.target_folder="path/to/folder"
```

## `ListFilesAction` (from `actions\ListFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `folder` | `str` | `` | folder to list the files from into a Buffer |
| `pattern` | `str` | `` | paatern to look for in file names |
| `extension` | `str` | `` | extension to include |
| `newer_than_seconds` | `int` | `` | specifies how old in seconds a file can be to be included |


```python
# Example usage of `ListFilesAction`
from pydatagrabber import ListFilesAction  # Adjust import if needed

obj = ListFilesAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.folder="path/to/folder"
obj.pattern="<string>"
obj.extension="<string>"
obj.newer_than_seconds=1
```

## `MailAction` (from `actions\MailAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
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

obj = MailAction()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
obj.smtp_server="<string>"
obj.port=1
obj.mail_account="<string>"
obj.pw="<string>"
obj.recipient="<string>"
obj.subject="<string>"
obj.body="<string>"
```

## `MoveFilesAction` (from `actions\MoveFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `target_folder` | `str` | `` | target folder to move all the files to in Buffer |


```python
# Example usage of `MoveFilesAction`
from pydatagrabber import MoveFilesAction  # Adjust import if needed

obj = MoveFilesAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.target_folder="path/to/folder"
```

## `ReadCsvAction` (from `actions\ReadCsvAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `file_path` | `str` | `` | path to the csv file to read the data from |
| `delimiter` | `str` | `';'` | delimiter character(s) for this csv file |


```python
# Example usage of `ReadCsvAction`
from pydatagrabber import ReadCsvAction  # Adjust import if needed

obj = ReadCsvAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.file_path="path/to/file.txt"
obj.delimiter=';'
```

## `ReadJsonAction` (from `actions\ReadJsonAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `file_path` | `str` | `` | path to the json file to read the data from |
| `json_path` | `str` | `` |  |


```python
# Example usage of `ReadJsonAction`
from pydatagrabber import ReadJsonAction  # Adjust import if needed

obj = ReadJsonAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.file_path="path/to/file.txt"
obj.json_path="<string>"
```

## `SetElementAction` (from `actions\SetElementAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `xpath` | `str` | `` | XPath definition to locate the element to set a value to |


```python
# Example usage of `SetElementAction`
from pydatagrabber import SetElementAction  # Adjust import if needed

obj = SetElementAction()
obj.child_ids='list()()'
obj.service_id="<string>"
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.xpath="<string>"
```

## `SleepAction` (from `actions\SleepAction.py`)

An action that sleeps for a specified number of seconds.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `SleepAction`
from pydatagrabber import SleepAction  # Adjust import if needed

obj = SleepAction()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `StartAction` (from `actions\StartAction.py`)

An action that starts the state machine.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `StartAction`
from pydatagrabber import StartAction  # Adjust import if needed

obj = StartAction()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `StopAction` (from `actions\StopAction.py`)

An action that stops the state machine.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `StopAction`
from pydatagrabber import StopAction  # Adjust import if needed

obj = StopAction()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `UrlNavigateAction` (from `actions\UrlNavigateAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `url` | `str` | `` | url to navigate to in browser |


```python
# Example usage of `UrlNavigateAction`
from pydatagrabber import UrlNavigateAction  # Adjust import if needed

obj = UrlNavigateAction()
obj.child_ids='list()()'
obj.service_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.url="https://example.com"
```

## `BufferInRangeTransition` (from `transitions\BufferInRangeTransition.py`)

A transition that compares the current buffer with a target value.
If the buffer matches the target, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `comparator` | `str` | `` | The comparison operator to use. |
| `value` | `any` | `` | The value to compare against the buffer. |


```python
# Example usage of `BufferInRangeTransition`
from pydatagrabber import BufferInRangeTransition  # Adjust import if needed

obj = BufferInRangeTransition()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.comparator="<string>"
obj.value="<value>"
```

## `CompareBufferTransition` (from `transitions\CompareBufferTransition.py`)

A transition that compares the current buffer with a target value.
If the buffer matches the target, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `comparator` | `str` | `` | The comparison operator to use. |
| `value` | `any` | `` | The value to compare against the buffer. |


```python
# Example usage of `CompareBufferTransition`
from pydatagrabber import CompareBufferTransition  # Adjust import if needed

obj = CompareBufferTransition()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.comparator="<string>"
obj.value="<value>"
```

## `FalseTransition` (from `transitions\FalseTransition.py`)

A transition that always returns False.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `FalseTransition`
from pydatagrabber import FalseTransition  # Adjust import if needed

obj = FalseTransition()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `TrueTransition` (from `transitions\TrueTransition.py`)

A transition that always returns True.
This is used to test the statemachine without any conditions.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `TrueTransition`
from pydatagrabber import TrueTransition  # Adjust import if needed

obj = TrueTransition()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```
