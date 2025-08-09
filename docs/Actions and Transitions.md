# Actions and Transitions Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Action`](#action-in-pydagstatemachineactionpy) |  |
| [`AdapterNode`](#adapternode-in-pydagstatemachineadapternodepy) | AdapterNode is a specialized BufferNode that integrates an adapter for data processing.It inherits from BufferNode to manage buffers and provides methods to interact with the adapter. |
| [`AgentNode`](#agentnode-in-pydagstatemachineagentnodepy) |  |
| [`BufferNode`](#buffernode-in-pydagstatemachinebuffernodepy) |  |
| [`JoinTransition`](#jointransition-in-pydagstatemachinejointransitionpy) |  |
| [`MappingNode`](#mappingnode-in-pydagstatemachinemappingnodepy) |  |
| [`Node`](#node-in-pydagstatemachinenodepy) |  |
| [`ServiceNode`](#servicenode-in-pydagstatemachineservicenodepy) | A class representing a service node in a state machine.Inherits from Node and adds functionality specific to service nodes. |
| [`Transition`](#transition-in-pydagstatemachinetransitionpy) |  |
| [`ConfigureElementAction`](#configureelementaction-in-pydagstatemachineactionsconfigureelementactionpy) | this `Action` configures a `GrabberElement` property by the provided `element_id` and name of the `option`, which is the class' property<br>the new property value is derived from the `Node`'s `buffer`Args:    GrabberNode (_type_): inherits from class GrabberNode    BufferNode (_type_): inherits from class BufferNodeRaises:    StatemachineException: if an error occurs during execute |
| [`MailAction`](#mailaction-in-pydagstatemachineactionsmailactionpy) |  |
| [`SleepAction`](#sleepaction-in-pydagstatemachineactionssleepactionpy) | An action that sleeps for a specified number of seconds. |
| [`StartAction`](#startaction-in-pydagstatemachineactionsstartactionpy) | An action that starts the state machine. |
| [`StopAction`](#stopaction-in-pydagstatemachineactionsstopactionpy) | An action that stops the state machine. |
| [`AdapterReadAction`](#adapterreadaction-in-pydagstatemachineactionsadaptersadapterreadactionpy) | Action to read data from an adapter. |
| [`AdapterWriteAction`](#adapterwriteaction-in-pydagstatemachineactionsadaptersadapterwriteactionpy) | Action to write data with an adapter. |
| [`BrowserAutomationAction`](#browserautomationaction-in-pydagstatemachineactionsbrowserbrowserautomationactionpy) |  |
| [`BrowserSetElementAction`](#browsersetelementaction-in-pydagstatemachineactionsbrowserbrowsersetelementactionpy) |  |
| [`BrowserUrlNavigateAction`](#browserurlnavigateaction-in-pydagstatemachineactionsbrowserbrowserurlnavigateactionpy) |  |
| [`AddBufferAction`](#addbufferaction-in-pydagstatemachineactionsbuffersaddbufferactionpy) | Action to add a buffer to the agent node. |
| [`BufferExtractAction`](#bufferextractaction-in-pydagstatemachineactionsbuffersbufferextractactionpy) | `Action` for extracting data from the parents' buffers to store into this buffer.This `Action` can only be applied on if the parents' buffers is of type `DictBuffer`. |
| [`FormattedStringAction`](#formattedstringaction-in-pydagstatemachineactionsbuffersformattedstringactionpy) | `Action` to compose a formatted string and store it in this `Action`'s bufferusing its parent's buffer to create the new string |
| [`LinkBufferAction`](#linkbufferaction-in-pydagstatemachineactionsbufferslinkbufferactionpy) | `Action` that's only function is to link a buffer from agent to the statemachinetherefore an empty execute method is provided |
| [`CopyFilesAction`](#copyfilesaction-in-pydagstatemachineactionsdocumentscopyfilesactionpy) |  |
| [`ListFilesAction`](#listfilesaction-in-pydagstatemachineactionsdocumentslistfilesactionpy) |  |
| [`MoveFilesAction`](#movefilesaction-in-pydagstatemachineactionsdocumentsmovefilesactionpy) |  |
| [`ReadCsvAction`](#readcsvaction-in-pydagstatemachineactionsdocumentsreadcsvactionpy) |  |
| [`ReadJsonAction`](#readjsonaction-in-pydagstatemachineactionsdocumentsreadjsonactionpy) |  |
| [`BufferEmptyTransition`](#bufferemptytransition-in-pydagstatemachinetransitionsbufferemptytransitionpy) | A transition that checks if specified buffer is empty.If the buffer is empty, the transition is successful. |
| [`BufferInRangeTransition`](#bufferinrangetransition-in-pydagstatemachinetransitionsbufferinrangetransitionpy) | A transition that compares the current buffer with a target value.If the buffer matches the target, the transition is successful. |
| [`BufferNotEmptyTransition`](#buffernotemptytransition-in-pydagstatemachinetransitionsbuffernotemptytransitionpy) | A transition that checks if specified buffer is not empty.If the buffer is not empty, the transition is successful. |
| [`CompareBufferTransition`](#comparebuffertransition-in-pydagstatemachinetransitionscomparebuffertransitionpy) | A transition that compares the current buffer with a target value.If the buffer matches the target, the transition is successful. |
| [`FalseTransition`](#falsetransition-in-pydagstatemachinetransitionsfalsetransitionpy) | A transition that always returns False. |
| [`TrueTransition`](#truetransition-in-pydagstatemachinetransitionstruetransitionpy) | A transition that always returns True.This is used to test the statemachine without any conditions. |



## `Action` (in `pydag\statemachine\Action.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Action`
from pydag.statemachine.Action import Action  # Adjust import if needed

obj = Action()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `AdapterNode` (in `pydag\statemachine\AdapterNode.py`)

AdapterNode is a specialized BufferNode that integrates an adapter for data processing.
It inherits from BufferNode to manage buffers and provides methods to interact with the adapter.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `adapter_id` | `str` | `` | ID of the adapter |


```python
# Example usage of `AdapterNode`
from pydag.statemachine.AdapterNode import AdapterNode  # Adjust import if needed

obj = AdapterNode()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.adapter_id="<string>"
```

[Go to Summary](#summary)
## `AgentNode` (in `pydag\statemachine\AgentNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `AgentNode`
from pydag.statemachine.AgentNode import AgentNode  # Adjust import if needed

obj = AgentNode()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `BufferNode` (in `pydag\statemachine\BufferNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `buffer_id` | `str` | `` | unique ID of the buffer |


```python
# Example usage of `BufferNode`
from pydag.statemachine.BufferNode import BufferNode  # Adjust import if needed

obj = BufferNode()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.buffer_id="<string>"
```

[Go to Summary](#summary)
## `JoinTransition` (in `pydag\statemachine\JoinTransition.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `JoinTransition`
from pydag.statemachine.JoinTransition import JoinTransition  # Adjust import if needed

obj = JoinTransition()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `MappingNode` (in `pydag\statemachine\MappingNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `mapping_id` | `str` | `` | ID of the mapping |


```python
# Example usage of `MappingNode`
from pydag.statemachine.MappingNode import MappingNode  # Adjust import if needed

obj = MappingNode()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.mapping_id="<string>"
```

[Go to Summary](#summary)
## `Node` (in `pydag\statemachine\Node.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |


```python
# Example usage of `Node`
from pydag.statemachine.Node import Node  # Adjust import if needed

obj = Node()
obj.id="<string>"
obj.load_on_install=False
obj.child_ids='list()'
```

[Go to Summary](#summary)
## `ServiceNode` (in `pydag\statemachine\ServiceNode.py`)

A class representing a service node in a state machine.
Inherits from Node and adds functionality specific to service nodes.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `service_id` | `str` | `` | ID of the service |


```python
# Example usage of `ServiceNode`
from pydag.statemachine.ServiceNode import ServiceNode  # Adjust import if needed

obj = ServiceNode()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.service_id="<string>"
```

[Go to Summary](#summary)
## `Transition` (in `pydag\statemachine\Transition.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Transition`
from pydag.statemachine.Transition import Transition  # Adjust import if needed

obj = Transition()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `ConfigureElementAction` (in `pydag\statemachine\actions\ConfigureElementAction.py`)

this `Action` configures a `GrabberElement` property by the provided `element_id` and name of the `option`, which is the class' property
<br>the new property value is derived from the `Node`'s `buffer`

Args:
    GrabberNode (_type_): inherits from class GrabberNode
    BufferNode (_type_): inherits from class BufferNode

Raises:
    StatemachineException: if an error occurs during execute
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `option` | `str` | `` | option to configure with new value |
| `element_id` | `str` | `` | id of the element to change the option for |
| `n` | `int` | `1` | specifies the number of samples to remove from buffer |


```python
# Example usage of `ConfigureElementAction`
from pydag.statemachine.actions.ConfigureElementAction import ConfigureElementAction  # Adjust import if needed

obj = ConfigureElementAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.option="<string>"
obj.element_id="<string>"
obj.n=1
```

[Go to Summary](#summary)
## `MailAction` (in `pydag\statemachine\actions\MailAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `smtp_server` | `str` | `` | host of the mail server to use |
| `port` | `int` | `` | port of the smtp server |
| `mail_account` | `str` | `` | mail account to use for login |
| `pw` | `str` | `` | password of the mail server |
| `recipient` | `str` | `` | mail address of the recipient |
| `subject` | `str` | `` | subject of the mail |
| `body` | `str` | `` | body of the mail |
| `tls` | `bool` | `True` | use TLS for the connection |


```python
# Example usage of `MailAction`
from pydag.statemachine.actions.MailAction import MailAction  # Adjust import if needed

obj = MailAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.smtp_server="<string>"
obj.port=1
obj.mail_account="<string>"
obj.pw="<string>"
obj.recipient="<string>"
obj.subject="<string>"
obj.body="<string>"
obj.tls=True
```

[Go to Summary](#summary)
## `SleepAction` (in `pydag\statemachine\actions\SleepAction.py`)

An action that sleeps for a specified number of seconds.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `sleep_time` | `int` | `0` | number of seconds to sleep for |


```python
# Example usage of `SleepAction`
from pydag.statemachine.actions.SleepAction import SleepAction  # Adjust import if needed

obj = SleepAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.sleep_time=0
```

[Go to Summary](#summary)
## `StartAction` (in `pydag\statemachine\actions\StartAction.py`)

An action that starts the state machine.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `StartAction`
from pydag.statemachine.actions.StartAction import StartAction  # Adjust import if needed

obj = StartAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `StopAction` (in `pydag\statemachine\actions\StopAction.py`)

An action that stops the state machine.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `StopAction`
from pydag.statemachine.actions.StopAction import StopAction  # Adjust import if needed

obj = StopAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `AdapterReadAction` (in `pydag\statemachine\actions\adapters\AdapterReadAction.py`)

Action to read data from an adapter.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `adapter_id` | `str` | `` | ID of the adapter |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `address` | `str` | `` | The address to read from the adapter. |
| `n` | `int` | `1` | The number of samples to read. |


```python
# Example usage of `AdapterReadAction`
from pydag.statemachine.actions.adapters.AdapterReadAction import AdapterReadAction  # Adjust import if needed

obj = AdapterReadAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.adapter_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.address="<string>"
obj.n=1
```

[Go to Summary](#summary)
## `AdapterWriteAction` (in `pydag\statemachine\actions\adapters\AdapterWriteAction.py`)

Action to write data with an adapter.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `adapter_id` | `str` | `` | ID of the adapter |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `address` | `str` | `` | The address to read from the adapter. |
| `n` | `int` | `1` | The number of samples to read. |
| `persistent` | `bool` | `False` | If True, the data will be stored in a persistent buffer. |


```python
# Example usage of `AdapterWriteAction`
from pydag.statemachine.actions.adapters.AdapterWriteAction import AdapterWriteAction  # Adjust import if needed

obj = AdapterWriteAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.adapter_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.address="<string>"
obj.n=1
obj.persistent=False
```

[Go to Summary](#summary)
## `BrowserAutomationAction` (in `pydag\statemachine\actions\browser\BrowserAutomationAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |


```python
# Example usage of `BrowserAutomationAction`
from pydag.statemachine.actions.browser.BrowserAutomationAction import BrowserAutomationAction  # Adjust import if needed

obj = BrowserAutomationAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.service_id="<string>"
```

[Go to Summary](#summary)
## `BrowserSetElementAction` (in `pydag\statemachine\actions\browser\BrowserSetElementAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `xpath` | `str` | `` | XPath definition to locate the element to set a value to |


```python
# Example usage of `BrowserSetElementAction`
from pydag.statemachine.actions.browser.BrowserSetElementAction import BrowserSetElementAction  # Adjust import if needed

obj = BrowserSetElementAction()
obj.child_ids='list()'
obj.service_id="<string>"
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.xpath="<string>"
```

[Go to Summary](#summary)
## `BrowserUrlNavigateAction` (in `pydag\statemachine\actions\browser\BrowserUrlNavigateAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `url` | `str` | `` | url to navigate to in browser |


```python
# Example usage of `BrowserUrlNavigateAction`
from pydag.statemachine.actions.browser.BrowserUrlNavigateAction import BrowserUrlNavigateAction  # Adjust import if needed

obj = BrowserUrlNavigateAction()
obj.child_ids='list()'
obj.service_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.url="https://example.com"
```

[Go to Summary](#summary)
## `AddBufferAction` (in `pydag\statemachine\actions\buffers\AddBufferAction.py`)

Action to add a buffer to the agent node.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `config` | `dict` | `` | Configuration for the buffer to be added. |


```python
# Example usage of `AddBufferAction`
from pydag.statemachine.actions.buffers.AddBufferAction import AddBufferAction  # Adjust import if needed

obj = AddBufferAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.config={}
```

[Go to Summary](#summary)
## `BufferExtractAction` (in `pydag\statemachine\actions\buffers\BufferExtractAction.py`)

`Action` for extracting data from the parents' buffers to store into this buffer.
This `Action` can only be applied on if the parents' buffers is of type `DictBuffer`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `extract_keys` | `list[str]` | `'list()'` | keys to search for in the parent buffers and extract their values into this element's buffer |


```python
# Example usage of `BufferExtractAction`
from pydag.statemachine.actions.buffers.BufferExtractAction import BufferExtractAction  # Adjust import if needed

obj = BufferExtractAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.extract_keys='list()'
```

[Go to Summary](#summary)
## `FormattedStringAction` (in `pydag\statemachine\actions\buffers\FormattedStringAction.py`)

`Action` to compose a formatted string and store it in this `Action`'s buffer
using its parent's buffer to create the new string
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `data_keys` | `list[str]` | `'list()'` | list of keys to use to compose the formatted string |
| `template` | `str` | `` | string template to insert the data from the parent buffer into, e.g. 'Hi {}, are you from {}' |


```python
# Example usage of `FormattedStringAction`
from pydag.statemachine.actions.buffers.FormattedStringAction import FormattedStringAction  # Adjust import if needed

obj = FormattedStringAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.data_keys='list()'
obj.template="<string>"
```

[Go to Summary](#summary)
## `LinkBufferAction` (in `pydag\statemachine\actions\buffers\LinkBufferAction.py`)

`Action` that's only function is to link a buffer from agent to the statemachine
therefore an empty execute method is provided
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `LinkBufferAction`
from pydag.statemachine.actions.buffers.LinkBufferAction import LinkBufferAction  # Adjust import if needed

obj = LinkBufferAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `CopyFilesAction` (in `pydag\statemachine\actions\documents\CopyFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `target_folder` | `str` | `` | target folder to copy all the files to in Buffer |


```python
# Example usage of `CopyFilesAction`
from pydag.statemachine.actions.documents.CopyFilesAction import CopyFilesAction  # Adjust import if needed

obj = CopyFilesAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.target_folder="path/to/folder"
```

[Go to Summary](#summary)
## `ListFilesAction` (in `pydag\statemachine\actions\documents\ListFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
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
from pydag.statemachine.actions.documents.ListFilesAction import ListFilesAction  # Adjust import if needed

obj = ListFilesAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.folder="path/to/folder"
obj.pattern="<string>"
obj.extension="<string>"
obj.newer_than_seconds=1
obj.recursive=False
```

[Go to Summary](#summary)
## `MoveFilesAction` (in `pydag\statemachine\actions\documents\MoveFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `target_folder` | `str` | `` | target folder to move all the files to in Buffer |


```python
# Example usage of `MoveFilesAction`
from pydag.statemachine.actions.documents.MoveFilesAction import MoveFilesAction  # Adjust import if needed

obj = MoveFilesAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.target_folder="path/to/folder"
```

[Go to Summary](#summary)
## `ReadCsvAction` (in `pydag\statemachine\actions\documents\ReadCsvAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `file_path` | `str` | `` | path to the csv file to read the data from |
| `delimiter` | `str` | `';'` | delimiter character(s) for this csv file |


```python
# Example usage of `ReadCsvAction`
from pydag.statemachine.actions.documents.ReadCsvAction import ReadCsvAction  # Adjust import if needed

obj = ReadCsvAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.file_path="path/to/file.txt"
obj.delimiter=';'
```

[Go to Summary](#summary)
## `ReadJsonAction` (in `pydag\statemachine\actions\documents\ReadJsonAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `file_path` | `str` | `` | path to the json file to read the data from |
| `json_path` | `str` | `` |  |


```python
# Example usage of `ReadJsonAction`
from pydag.statemachine.actions.documents.ReadJsonAction import ReadJsonAction  # Adjust import if needed

obj = ReadJsonAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.file_path="path/to/file.txt"
obj.json_path="<string>"
```

[Go to Summary](#summary)
## `BufferEmptyTransition` (in `pydag\statemachine\transitions\BufferEmptyTransition.py`)

A transition that checks if specified buffer is empty.
If the buffer is empty, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `BufferEmptyTransition`
from pydag.statemachine.transitions.BufferEmptyTransition import BufferEmptyTransition  # Adjust import if needed

obj = BufferEmptyTransition()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `BufferInRangeTransition` (in `pydag\statemachine\transitions\BufferInRangeTransition.py`)

A transition that compares the current buffer with a target value.
If the buffer matches the target, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `comparator` | `str` | `` | The comparison operator to use. |
| `value` | `any` | `` | The value to compare against the buffer. |


```python
# Example usage of `BufferInRangeTransition`
from pydag.statemachine.transitions.BufferInRangeTransition import BufferInRangeTransition  # Adjust import if needed

obj = BufferInRangeTransition()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.comparator="<string>"
obj.value="<value>"
```

[Go to Summary](#summary)
## `BufferNotEmptyTransition` (in `pydag\statemachine\transitions\BufferNotEmptyTransition.py`)

A transition that checks if specified buffer is not empty.
If the buffer is not empty, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `BufferNotEmptyTransition`
from pydag.statemachine.transitions.BufferNotEmptyTransition import BufferNotEmptyTransition  # Adjust import if needed

obj = BufferNotEmptyTransition()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `CompareBufferTransition` (in `pydag\statemachine\transitions\CompareBufferTransition.py`)

A transition that compares the current buffer with a target value.
If the buffer matches the target, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `comparator` | `str` | `` | The comparison operator to use. |
| `value` | `any` | `` | The value to compare against the buffer. |


```python
# Example usage of `CompareBufferTransition`
from pydag.statemachine.transitions.CompareBufferTransition import CompareBufferTransition  # Adjust import if needed

obj = CompareBufferTransition()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.comparator="<string>"
obj.value="<value>"
```

[Go to Summary](#summary)
## `FalseTransition` (in `pydag\statemachine\transitions\FalseTransition.py`)

A transition that always returns False.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `FalseTransition`
from pydag.statemachine.transitions.FalseTransition import FalseTransition  # Adjust import if needed

obj = FalseTransition()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `TrueTransition` (in `pydag\statemachine\transitions\TrueTransition.py`)

A transition that always returns True.
This is used to test the statemachine without any conditions.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `TrueTransition`
from pydag.statemachine.transitions.TrueTransition import TrueTransition  # Adjust import if needed

obj = TrueTransition()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)