# Actions and Transitions Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Action`](#action-in-pydgstatemachineactionpy) |  |
| [`AdapterNode`](#adapternode-in-pydgstatemachineadapternodepy) | AdapterNode is a specialized BufferNode that integrates an adapter for data processing.It inherits from BufferNode to manage buffers and provides methods to interact with the adapter. |
| [`BufferNode`](#buffernode-in-pydgstatemachinebuffernodepy) |  |
| [`GrabberNode`](#grabbernode-in-pydgstatemachinegrabbernodepy) |  |
| [`JoinTransition`](#jointransition-in-pydgstatemachinejointransitionpy) |  |
| [`MappingNode`](#mappingnode-in-pydgstatemachinemappingnodepy) |  |
| [`Node`](#node-in-pydgstatemachinenodepy) |  |
| [`ServiceNode`](#servicenode-in-pydgstatemachineservicenodepy) | A class representing a service node in a state machine.Inherits from Node and adds functionality specific to service nodes. |
| [`Transition`](#transition-in-pydgstatemachinetransitionpy) |  |
| [`AdapterReadAction`](#adapterreadaction-in-pydgstatemachineactionsadapterreadactionpy) | Action to read data from an adapter. |
| [`AdapterWriteAction`](#adapterwriteaction-in-pydgstatemachineactionsadapterwriteactionpy) | Action to write data with an adapter. |
| [`AddBufferAction`](#addbufferaction-in-pydgstatemachineactionsaddbufferactionpy) | Action to add a buffer to the grabber node. |
| [`BrowserAutomationAction`](#browserautomationaction-in-pydgstatemachineactionsbrowserautomationactionpy) |  |
| [`BrowserSetElementAction`](#browsersetelementaction-in-pydgstatemachineactionsbrowsersetelementactionpy) |  |
| [`BrowserUrlNavigateAction`](#browserurlnavigateaction-in-pydgstatemachineactionsbrowserurlnavigateactionpy) |  |
| [`ConfigureElementAction`](#configureelementaction-in-pydgstatemachineactionsconfigureelementactionpy) | this `Action` configures a `GrabberElement` property by the provided `element_id` and name of the `option`, which is the class' property<br>the new property value is derived from the `Node`'s `buffer`Args:    GrabberNode (_type_): inherits from class GrabberNode    BufferNode (_type_): inherits from class BufferNodeRaises:    StatemachineException: if an error occurs during execute |
| [`CopyFilesAction`](#copyfilesaction-in-pydgstatemachineactionscopyfilesactionpy) |  |
| [`ListFilesAction`](#listfilesaction-in-pydgstatemachineactionslistfilesactionpy) |  |
| [`MailAction`](#mailaction-in-pydgstatemachineactionsmailactionpy) |  |
| [`MoveFilesAction`](#movefilesaction-in-pydgstatemachineactionsmovefilesactionpy) |  |
| [`ReadCsvAction`](#readcsvaction-in-pydgstatemachineactionsreadcsvactionpy) |  |
| [`ReadJsonAction`](#readjsonaction-in-pydgstatemachineactionsreadjsonactionpy) |  |
| [`SleepAction`](#sleepaction-in-pydgstatemachineactionssleepactionpy) | An action that sleeps for a specified number of seconds. |
| [`StartAction`](#startaction-in-pydgstatemachineactionsstartactionpy) | An action that starts the state machine. |
| [`StopAction`](#stopaction-in-pydgstatemachineactionsstopactionpy) | An action that stops the state machine. |
| [`BufferInRangeTransition`](#bufferinrangetransition-in-pydgstatemachinetransitionsbufferinrangetransitionpy) | A transition that compares the current buffer with a target value.If the buffer matches the target, the transition is successful. |
| [`CompareBufferTransition`](#comparebuffertransition-in-pydgstatemachinetransitionscomparebuffertransitionpy) | A transition that compares the current buffer with a target value.If the buffer matches the target, the transition is successful. |
| [`FalseTransition`](#falsetransition-in-pydgstatemachinetransitionsfalsetransitionpy) | A transition that always returns False. |
| [`TrueTransition`](#truetransition-in-pydgstatemachinetransitionstruetransitionpy) | A transition that always returns True.This is used to test the statemachine without any conditions. |



## `Action` (in `pydg\statemachine\Action.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Action`
from pydg.statemachine.Action import Action  # Adjust import if needed

obj = Action()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `AdapterNode` (in `pydg\statemachine\AdapterNode.py`)

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
from pydg.statemachine.AdapterNode import AdapterNode  # Adjust import if needed

obj = AdapterNode()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.adapter_id="<string>"
```

## `BufferNode` (in `pydg\statemachine\BufferNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `buffer_id` | `str` | `` | unique ID of the buffer |


```python
# Example usage of `BufferNode`
from pydg.statemachine.BufferNode import BufferNode  # Adjust import if needed

obj = BufferNode()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
obj.buffer_id="<string>"
```

## `GrabberNode` (in `pydg\statemachine\GrabberNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `GrabberNode`
from pydg.statemachine.GrabberNode import GrabberNode  # Adjust import if needed

obj = GrabberNode()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `JoinTransition` (in `pydg\statemachine\JoinTransition.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `JoinTransition`
from pydg.statemachine.JoinTransition import JoinTransition  # Adjust import if needed

obj = JoinTransition()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `MappingNode` (in `pydg\statemachine\MappingNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `mapping_id` | `str` | `` | ID of the mapping |


```python
# Example usage of `MappingNode`
from pydg.statemachine.MappingNode import MappingNode  # Adjust import if needed

obj = MappingNode()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
obj.mapping_id="<string>"
```

## `Node` (in `pydg\statemachine\Node.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |


```python
# Example usage of `Node`
from pydg.statemachine.Node import Node  # Adjust import if needed

obj = Node()
obj.id="<string>"
obj.load_on_install=False
obj.child_ids='list()()'
```

## `ServiceNode` (in `pydg\statemachine\ServiceNode.py`)

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
from pydg.statemachine.ServiceNode import ServiceNode  # Adjust import if needed

obj = ServiceNode()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
obj.service_id="<string>"
```

## `Transition` (in `pydg\statemachine\Transition.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Transition`
from pydg.statemachine.Transition import Transition  # Adjust import if needed

obj = Transition()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `AdapterReadAction` (in `pydg\statemachine\actions\AdapterReadAction.py`)

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
from pydg.statemachine.actions.AdapterReadAction import AdapterReadAction  # Adjust import if needed

obj = AdapterReadAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.adapter_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.address="<string>"
obj.n=1
```

## `AdapterWriteAction` (in `pydg\statemachine\actions\AdapterWriteAction.py`)

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
from pydg.statemachine.actions.AdapterWriteAction import AdapterWriteAction  # Adjust import if needed

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

## `AddBufferAction` (in `pydg\statemachine\actions\AddBufferAction.py`)

Action to add a buffer to the grabber node.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `config` | `dict` | `` | Configuration for the buffer to be added. |


```python
# Example usage of `AddBufferAction`
from pydg.statemachine.actions.AddBufferAction import AddBufferAction  # Adjust import if needed

obj = AddBufferAction()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
obj.config={}
```

## `BrowserAutomationAction` (in `pydg\statemachine\actions\BrowserAutomationAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |


```python
# Example usage of `BrowserAutomationAction`
from pydg.statemachine.actions.BrowserAutomationAction import BrowserAutomationAction  # Adjust import if needed

obj = BrowserAutomationAction()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
obj.service_id="<string>"
```

## `BrowserSetElementAction` (in `pydg\statemachine\actions\BrowserSetElementAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `xpath` | `str` | `` | XPath definition to locate the element to set a value to |


```python
# Example usage of `BrowserSetElementAction`
from pydg.statemachine.actions.BrowserSetElementAction import BrowserSetElementAction  # Adjust import if needed

obj = BrowserSetElementAction()
obj.child_ids='list()()'
obj.service_id="<string>"
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.xpath="<string>"
```

## `BrowserUrlNavigateAction` (in `pydg\statemachine\actions\BrowserUrlNavigateAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `url` | `str` | `` | url to navigate to in browser |


```python
# Example usage of `BrowserUrlNavigateAction`
from pydg.statemachine.actions.BrowserUrlNavigateAction import BrowserUrlNavigateAction  # Adjust import if needed

obj = BrowserUrlNavigateAction()
obj.child_ids='list()()'
obj.service_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.url="https://example.com"
```

## `ConfigureElementAction` (in `pydg\statemachine\actions\ConfigureElementAction.py`)

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
from pydg.statemachine.actions.ConfigureElementAction import ConfigureElementAction  # Adjust import if needed

obj = ConfigureElementAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.option="<string>"
obj.element_id="<string>"
obj.n=1
```

## `CopyFilesAction` (in `pydg\statemachine\actions\CopyFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `target_folder` | `str` | `` | target folder to copy all the files to in Buffer |


```python
# Example usage of `CopyFilesAction`
from pydg.statemachine.actions.CopyFilesAction import CopyFilesAction  # Adjust import if needed

obj = CopyFilesAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.target_folder="path/to/folder"
```

## `ListFilesAction` (in `pydg\statemachine\actions\ListFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `folder` | `str` | `` | folder to list the files from into a Buffer |
| `pattern` | `str` | `` | pattern to look for in file names |
| `extension` | `str` | `` | extension to include |
| `newer_than_seconds` | `int` | `` | specifies how old in seconds a file can be to be included |
| `recursive` | `bool` | `False` | specifies whether to search subdirectories aswell |


```python
# Example usage of `ListFilesAction`
from pydg.statemachine.actions.ListFilesAction import ListFilesAction  # Adjust import if needed

obj = ListFilesAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.folder="path/to/folder"
obj.pattern="<string>"
obj.extension="<string>"
obj.newer_than_seconds=1
obj.recursive=False
```

## `MailAction` (in `pydg\statemachine\actions\MailAction.py`)

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
from pydg.statemachine.actions.MailAction import MailAction  # Adjust import if needed

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

## `MoveFilesAction` (in `pydg\statemachine\actions\MoveFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `target_folder` | `str` | `` | target folder to move all the files to in Buffer |


```python
# Example usage of `MoveFilesAction`
from pydg.statemachine.actions.MoveFilesAction import MoveFilesAction  # Adjust import if needed

obj = MoveFilesAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.target_folder="path/to/folder"
```

## `ReadCsvAction` (in `pydg\statemachine\actions\ReadCsvAction.py`)

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
from pydg.statemachine.actions.ReadCsvAction import ReadCsvAction  # Adjust import if needed

obj = ReadCsvAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.file_path="path/to/file.txt"
obj.delimiter=';'
```

## `ReadJsonAction` (in `pydg\statemachine\actions\ReadJsonAction.py`)

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
from pydg.statemachine.actions.ReadJsonAction import ReadJsonAction  # Adjust import if needed

obj = ReadJsonAction()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.file_path="path/to/file.txt"
obj.json_path="<string>"
```

## `SleepAction` (in `pydg\statemachine\actions\SleepAction.py`)

An action that sleeps for a specified number of seconds.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `sleep_time` | `int` | `0` | number of seconds to sleep for |


```python
# Example usage of `SleepAction`
from pydg.statemachine.actions.SleepAction import SleepAction  # Adjust import if needed

obj = SleepAction()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
obj.sleep_time=0
```

## `StartAction` (in `pydg\statemachine\actions\StartAction.py`)

An action that starts the state machine.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `StartAction`
from pydg.statemachine.actions.StartAction import StartAction  # Adjust import if needed

obj = StartAction()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `StopAction` (in `pydg\statemachine\actions\StopAction.py`)

An action that stops the state machine.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `StopAction`
from pydg.statemachine.actions.StopAction import StopAction  # Adjust import if needed

obj = StopAction()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `BufferInRangeTransition` (in `pydg\statemachine\transitions\BufferInRangeTransition.py`)

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
from pydg.statemachine.transitions.BufferInRangeTransition import BufferInRangeTransition  # Adjust import if needed

obj = BufferInRangeTransition()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.comparator="<string>"
obj.value="<value>"
```

## `CompareBufferTransition` (in `pydg\statemachine\transitions\CompareBufferTransition.py`)

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
from pydg.statemachine.transitions.CompareBufferTransition import CompareBufferTransition  # Adjust import if needed

obj = CompareBufferTransition()
obj.child_ids='list()()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.comparator="<string>"
obj.value="<value>"
```

## `FalseTransition` (in `pydg\statemachine\transitions\FalseTransition.py`)

A transition that always returns False.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `FalseTransition`
from pydg.statemachine.transitions.FalseTransition import FalseTransition  # Adjust import if needed

obj = FalseTransition()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```

## `TrueTransition` (in `pydg\statemachine\transitions\TrueTransition.py`)

A transition that always returns True.
This is used to test the statemachine without any conditions.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `TrueTransition`
from pydg.statemachine.transitions.TrueTransition import TrueTransition  # Adjust import if needed

obj = TrueTransition()
obj.child_ids='list()()'
obj.id="<string>"
obj.load_on_install=False
```
