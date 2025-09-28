# Actions and Transitions Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Action`](#action-in-pydagnodesactionpy) |  |
| [`AdapterNode`](#adapternode-in-pydagnodesadapternodepy) | AdapterNode is a specialized BufferNode that integrates an adapter for data processing.It inherits from BufferNode to manage buffers and provides methods to interact with the adapter. |
| [`AgentNode`](#agentnode-in-pydagnodesagentnodepy) |  |
| [`BufferNode`](#buffernode-in-pydagnodesbuffernodepy) |  |
| [`MappingNode`](#mappingnode-in-pydagnodesmappingnodepy) |  |
| [`Node`](#node-in-pydagnodesnodepy) |  |
| [`ServiceNode`](#servicenode-in-pydagnodesservicenodepy) | A class representing a service node in a state machine.Inherits from Node and adds functionality specific to service nodes. |
| [`Transition`](#transition-in-pydagnodestransitionpy) |  |
| [`AdapterReadAction`](#adapterreadaction-in-pydagnodesadaptersadapterreadactionpy) | Action to read data from an adapter. |
| [`AdapterWriteAction`](#adapterwriteaction-in-pydagnodesadaptersadapterwriteactionpy) | Action to write data with an adapter. |
| [`BrowserAutomationAction`](#browserautomationaction-in-pydagnodesbrowserbrowserautomationactionpy) |  |
| [`BrowserSetElementAction`](#browsersetelementaction-in-pydagnodesbrowserbrowsersetelementactionpy) |  |
| [`BrowserUrlNavigateAction`](#browserurlnavigateaction-in-pydagnodesbrowserbrowserurlnavigateactionpy) |  |
| [`AddBufferAction`](#addbufferaction-in-pydagnodesbuffersaddbufferactionpy) | Action to add a buffer to the agent node. |
| [`BufferEmptyTransition`](#bufferemptytransition-in-pydagnodesbuffersbufferemptytransitionpy) | A transition that checks if specified buffer is empty.If the buffer is empty, the transition is successful. |
| [`BufferExtractAction`](#bufferextractaction-in-pydagnodesbuffersbufferextractactionpy) | `Action` for extracting data from a specified buffer and to store the extracted data into this buffer.This `Action` can only be applied on if the specified buffer is of type `DictBuffer`. |
| [`BufferInRangeTransition`](#bufferinrangetransition-in-pydagnodesbuffersbufferinrangetransitionpy) | A transition that compares the current buffer with a target value.If the buffer matches the target, the transition is successful. |
| [`BufferNotEmptyTransition`](#buffernotemptytransition-in-pydagnodesbuffersbuffernotemptytransitionpy) | A transition that checks if specified buffer is not empty.If the buffer is not empty, the transition is successful. |
| [`ClearBufferAction`](#clearbufferaction-in-pydagnodesbuffersclearbufferactionpy) |  |
| [`CompareBufferTransition`](#comparebuffertransition-in-pydagnodesbufferscomparebuffertransitionpy) | A transition that compares the current buffer with a target value.If the buffer matches the target, the transition is successful. |
| [`DataFrameFilterAction`](#dataframefilteraction-in-pydagnodesbuffersdataframefilteractionpy) |  |
| [`FormattedStringAction`](#formattedstringaction-in-pydagnodesbuffersformattedstringactionpy) | `Action` to compose a formatted string and store it in this `Action`'s bufferusing its parent's buffer to create the new string |
| [`LinkBufferAction`](#linkbufferaction-in-pydagnodesbufferslinkbufferactionpy) | `Action` that's only function is to link a buffer from agent to the statemachinetherefore an empty execute method is provided |
| [`ParentBufferExtractAction`](#parentbufferextractaction-in-pydagnodesbuffersparentbufferextractactionpy) | `Action` for extracting data from the parents' buffers to store into this buffer.This `Action` can only be applied on if the parents' buffers is of type `DictBuffer`. |
| [`SampledSignalAction`](#sampledsignalaction-in-pydagnodesbufferssampledsignalactionpy) |  |
| [`ConvertFile2Base64Action`](#convertfile2base64action-in-pydagnodesdocumentsconvertfile2base64actionpy) |  |
| [`CopyFilesAction`](#copyfilesaction-in-pydagnodesdocumentscopyfilesactionpy) |  |
| [`ICalAction`](#icalaction-in-pydagnodesdocumentsicalactionpy) |  |
| [`ListFilesAction`](#listfilesaction-in-pydagnodesdocumentslistfilesactionpy) |  |
| [`MoveFilesAction`](#movefilesaction-in-pydagnodesdocumentsmovefilesactionpy) | `Action` that moves files to a new `target_folder`<br>this `Action` either needs a parent `Node` with a `ListBuffer` with filepaths or a reference to a `Buffer` via `buffer_id` or its `buffer`variableRaises:    StatemachineException: if folder does not exist or wrong `Buffer` is provided |
| [`PlotlifyAction`](#plotlifyaction-in-pydagnodesdocumentsplotlifyactionpy) |  |
| [`ReadCsvAction`](#readcsvaction-in-pydagnodesdocumentsreadcsvactionpy) |  |
| [`ReadExcelRangeAction`](#readexcelrangeaction-in-pydagnodesdocumentsreadexcelrangeactionpy) |  |
| [`ReadExcelTableAction`](#readexceltableaction-in-pydagnodesdocumentsreadexceltableactionpy) |  |
| [`ReadJsonAction`](#readjsonaction-in-pydagnodesdocumentsreadjsonactionpy) |  |
| [`ReadNpzAction`](#readnpzaction-in-pydagnodesdocumentsreadnpzactionpy) |  |
| [`HttpGetAction`](#httpgetaction-in-pydagnodeshttphttpgetactionpy) |  |
| [`HttpPostAction`](#httppostaction-in-pydagnodeshttphttppostactionpy) |  |
| [`ConfigureElementAction`](#configureelementaction-in-pydagnodesutilsconfigureelementactionpy) | this `Action` configures a `GrabberElement` property by the provided `element_id` and name of the `option`, which is the class' property<br>the new property value is derived from the `Node`'s `buffer`Args:    GrabberNode (_type_): inherits from class GrabberNode    BufferNode (_type_): inherits from class BufferNodeRaises:    StatemachineException: if an error occurs during execute |
| [`CountAction`](#countaction-in-pydagnodesutilscountactionpy) | Action that counts the number of times it has been called. |
| [`CountTransition`](#counttransition-in-pydagnodesutilscounttransitionpy) | A transition that counts the number of times it has been triggered. |
| [`FalseTransition`](#falsetransition-in-pydagnodesutilsfalsetransitionpy) | A transition that always returns False. |
| [`JoinTransition`](#jointransition-in-pydagnodesutilsjointransitionpy) |  |
| [`MailAction`](#mailaction-in-pydagnodesutilsmailactionpy) |  |
| [`PrintAction`](#printaction-in-pydagnodesutilsprintactionpy) | An action that prints a message when executed. |
| [`SleepAction`](#sleepaction-in-pydagnodesutilssleepactionpy) | An action that sleeps for a specified number of seconds. |
| [`SleepUntilAction`](#sleepuntilaction-in-pydagnodesutilssleepuntilactionpy) | An action that sleeps until the specified daytime. |
| [`StartAction`](#startaction-in-pydagnodesutilsstartactionpy) | An action that starts the state machine. |
| [`StopAction`](#stopaction-in-pydagnodesutilsstopactionpy) | An action that stops the state machine. |
| [`TrueTransition`](#truetransition-in-pydagnodesutilstruetransitionpy) | A transition that always returns True.This is used to test the statemachine without any conditions. |



## `Action` (in `pydag\nodes\Action.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Action`
from pydag.nodes.Action import Action  # Adjust import if needed

obj = Action()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `AdapterNode` (in `pydag\nodes\AdapterNode.py`)

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
from pydag.nodes.AdapterNode import AdapterNode  # Adjust import if needed

obj = AdapterNode()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.adapter_id="<string>"
```

[Go to Summary](#summary)
## `AgentNode` (in `pydag\nodes\AgentNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `AgentNode`
from pydag.nodes.AgentNode import AgentNode  # Adjust import if needed

obj = AgentNode()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `BufferNode` (in `pydag\nodes\BufferNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `buffer_id` | `str` | `` | unique ID of the buffer |


```python
# Example usage of `BufferNode`
from pydag.nodes.BufferNode import BufferNode  # Adjust import if needed

obj = BufferNode()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.buffer_id="<string>"
```

[Go to Summary](#summary)
## `MappingNode` (in `pydag\nodes\MappingNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `mapping_id` | `str` | `` | ID of the mapping |


```python
# Example usage of `MappingNode`
from pydag.nodes.MappingNode import MappingNode  # Adjust import if needed

obj = MappingNode()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.mapping_id="<string>"
```

[Go to Summary](#summary)
## `Node` (in `pydag\nodes\Node.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |


```python
# Example usage of `Node`
from pydag.nodes.Node import Node  # Adjust import if needed

obj = Node()
obj.id="<string>"
obj.load_on_install=False
obj.child_ids='list()'
```

[Go to Summary](#summary)
## `ServiceNode` (in `pydag\nodes\ServiceNode.py`)

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
from pydag.nodes.ServiceNode import ServiceNode  # Adjust import if needed

obj = ServiceNode()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.service_id="<string>"
```

[Go to Summary](#summary)
## `Transition` (in `pydag\nodes\Transition.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Transition`
from pydag.nodes.Transition import Transition  # Adjust import if needed

obj = Transition()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `AdapterReadAction` (in `pydag\nodes\adapters\AdapterReadAction.py`)

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
from pydag.nodes.adapters.AdapterReadAction import AdapterReadAction  # Adjust import if needed

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
## `AdapterWriteAction` (in `pydag\nodes\adapters\AdapterWriteAction.py`)

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
from pydag.nodes.adapters.AdapterWriteAction import AdapterWriteAction  # Adjust import if needed

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
## `BrowserAutomationAction` (in `pydag\nodes\browser\BrowserAutomationAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |


```python
# Example usage of `BrowserAutomationAction`
from pydag.nodes.browser.BrowserAutomationAction import BrowserAutomationAction  # Adjust import if needed

obj = BrowserAutomationAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.service_id="<string>"
```

[Go to Summary](#summary)
## `BrowserSetElementAction` (in `pydag\nodes\browser\BrowserSetElementAction.py`)

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
from pydag.nodes.browser.BrowserSetElementAction import BrowserSetElementAction  # Adjust import if needed

obj = BrowserSetElementAction()
obj.child_ids='list()'
obj.service_id="<string>"
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.xpath="<string>"
```

[Go to Summary](#summary)
## `BrowserUrlNavigateAction` (in `pydag\nodes\browser\BrowserUrlNavigateAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `url` | `str` | `` | url to navigate to in browser |


```python
# Example usage of `BrowserUrlNavigateAction`
from pydag.nodes.browser.BrowserUrlNavigateAction import BrowserUrlNavigateAction  # Adjust import if needed

obj = BrowserUrlNavigateAction()
obj.child_ids='list()'
obj.service_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.url="https://example.com"
```

[Go to Summary](#summary)
## `AddBufferAction` (in `pydag\nodes\buffers\AddBufferAction.py`)

Action to add a buffer to the agent node.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `config` | `dict` | `` | Configuration for the buffer to be added. |


```python
# Example usage of `AddBufferAction`
from pydag.nodes.buffers.AddBufferAction import AddBufferAction  # Adjust import if needed

obj = AddBufferAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.config={}
```

[Go to Summary](#summary)
## `BufferEmptyTransition` (in `pydag\nodes\buffers\BufferEmptyTransition.py`)

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
from pydag.nodes.buffers.BufferEmptyTransition import BufferEmptyTransition  # Adjust import if needed

obj = BufferEmptyTransition()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `BufferExtractAction` (in `pydag\nodes\buffers\BufferExtractAction.py`)

`Action` for extracting data from a specified buffer and to store the extracted data into this buffer.
This `Action` can only be applied on if the specified buffer is of type `DictBuffer`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `extract_buffer_id` | `str` | `` | id of the buffer to extract data from |
| `extract_keys` | `list[str]` | `'list()'` | keys to search for in the specified buffer and extract their values into this element's buffer |
| `persistent` | `bool` | `True` | specifies whether to keep the extracted data in origin buffer |
| `n` | `int` | `0` | number of samples to extract from buffer, default 0 extracts all |


```python
# Example usage of `BufferExtractAction`
from pydag.nodes.buffers.BufferExtractAction import BufferExtractAction  # Adjust import if needed

obj = BufferExtractAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.extract_buffer_id="<string>"
obj.extract_keys='list()'
obj.persistent=True
obj.n=0
```

[Go to Summary](#summary)
## `BufferInRangeTransition` (in `pydag\nodes\buffers\BufferInRangeTransition.py`)

A transition that compares the current buffer with a target value.
If the buffer matches the target, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `comparator` | `str` | `` | the comparison operator to use |
| `upper_limit` | `any` | `` | the upper limit of the range |
| `lower_limit` | `any` | `` | the lower limit of the range |


```python
# Example usage of `BufferInRangeTransition`
from pydag.nodes.buffers.BufferInRangeTransition import BufferInRangeTransition  # Adjust import if needed

obj = BufferInRangeTransition()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.comparator="<string>"
obj.upper_limit="<value>"
obj.lower_limit="<value>"
```

[Go to Summary](#summary)
## `BufferNotEmptyTransition` (in `pydag\nodes\buffers\BufferNotEmptyTransition.py`)

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
from pydag.nodes.buffers.BufferNotEmptyTransition import BufferNotEmptyTransition  # Adjust import if needed

obj = BufferNotEmptyTransition()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `ClearBufferAction` (in `pydag\nodes\buffers\ClearBufferAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `ClearBufferAction`
from pydag.nodes.buffers.ClearBufferAction import ClearBufferAction  # Adjust import if needed

obj = ClearBufferAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `CompareBufferTransition` (in `pydag\nodes\buffers\CompareBufferTransition.py`)

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
from pydag.nodes.buffers.CompareBufferTransition import CompareBufferTransition  # Adjust import if needed

obj = CompareBufferTransition()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.comparator="<string>"
obj.value="<value>"
```

[Go to Summary](#summary)
## `DataFrameFilterAction` (in `pydag\nodes\buffers\DataFrameFilterAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `row_filter` | `str` | `` | pandas filter command to apply to filter the rows of the buffer converted to dataframe |
| `column_filter` | `list[str]` | `'list()'` | list of columns to filter for |
| `persistent` | `bool` | `True` | specifies whether data is removed (False) from parent or not (True) |
| `n` | `int` | `0` | specifies how much data is retrieved from parent buffer. Default 0 -> all data |


```python
# Example usage of `DataFrameFilterAction`
from pydag.nodes.buffers.DataFrameFilterAction import DataFrameFilterAction  # Adjust import if needed

obj = DataFrameFilterAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.row_filter="<string>"
obj.column_filter='list()'
obj.persistent=True
obj.n=0
```

[Go to Summary](#summary)
## `FormattedStringAction` (in `pydag\nodes\buffers\FormattedStringAction.py`)

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
| `persistent` | `bool` | `False` | specifies whether to remove the data from parent buffers when retrieving the data |


```python
# Example usage of `FormattedStringAction`
from pydag.nodes.buffers.FormattedStringAction import FormattedStringAction  # Adjust import if needed

obj = FormattedStringAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.data_keys='list()'
obj.template="<string>"
obj.persistent=False
```

[Go to Summary](#summary)
## `LinkBufferAction` (in `pydag\nodes\buffers\LinkBufferAction.py`)

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
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction  # Adjust import if needed

obj = LinkBufferAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `ParentBufferExtractAction` (in `pydag\nodes\buffers\ParentBufferExtractAction.py`)

`Action` for extracting data from the parents' buffers to store into this buffer.
This `Action` can only be applied on if the parents' buffers is of type `DictBuffer`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `extract_keys` | `list[str]` | `'list()'` | keys to search for in the parent buffers and extract their values into this element's buffer |
| `persistent` | `bool` | `True` | specifies whether to keep the extracted data in origin buffer |
| `n` | `int` | `0` | number of samples to extract from buffer, default 0 extracts all |


```python
# Example usage of `ParentBufferExtractAction`
from pydag.nodes.buffers.ParentBufferExtractAction import ParentBufferExtractAction  # Adjust import if needed

obj = ParentBufferExtractAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.extract_keys='list()'
obj.persistent=True
obj.n=0
```

[Go to Summary](#summary)
## `SampledSignalAction` (in `pydag\nodes\buffers\SampledSignalAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `signal` | `SampledSignal` | `` |  |
| `n` | `int` | `1` |  |


```python
# Example usage of `SampledSignalAction`
from pydag.nodes.buffers.SampledSignalAction import SampledSignalAction  # Adjust import if needed

obj = SampledSignalAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.signal="<value>"
obj.n=1
```

[Go to Summary](#summary)
## `ConvertFile2Base64Action` (in `pydag\nodes\documents\ConvertFile2Base64Action.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `file_paths` | `list[str]` | `'list()'` | path to the file to convert to base64, e.g. PNG | JPG | PDF | MP4 | AVI | MOV | MP3 |
| `extract_parent_keys` | `list[str]` | `'list()'` | instead of directly specifying file_paths, this property can be used to retrieve the filepaths from a parent buffer |


```python
# Example usage of `ConvertFile2Base64Action`
from pydag.nodes.documents.ConvertFile2Base64Action import ConvertFile2Base64Action  # Adjust import if needed

obj = ConvertFile2Base64Action()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.file_paths='list()'
obj.extract_parent_keys='list()'
```

[Go to Summary](#summary)
## `CopyFilesAction` (in `pydag\nodes\documents\CopyFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `target_folder` | `str` | `` | target folder to copy all the files to in Buffer |


```python
# Example usage of `CopyFilesAction`
from pydag.nodes.documents.CopyFilesAction import CopyFilesAction  # Adjust import if needed

obj = CopyFilesAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.target_folder="path/to/folder"
```

[Go to Summary](#summary)
## `ICalAction` (in `pydag\nodes\documents\ICalAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `ical_path` | `str` | `` |  |
| `date_format` | `str` | `` |  |
| `name_key` | `str` | `` |  |
| `start_key` | `str` | `` |  |
| `end_key` | `str` | `` |  |
| `duration_unit` | `str` | `'hours'` |  |
| `duration_key` | `str` | `` |  |
| `description_key` | `str` | `` |  |
| `location_key` | `str` | `` |  |
| `time_zone` | `str` | `'Europe/Berlin'` |  |


```python
# Example usage of `ICalAction`
from pydag.nodes.documents.ICalAction import ICalAction  # Adjust import if needed

obj = ICalAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.ical_path="<string>"
obj.date_format="<string>"
obj.name_key="John Doe"
obj.start_key="<string>"
obj.end_key="<string>"
obj.duration_unit='hours'
obj.duration_key="<string>"
obj.description_key="<string>"
obj.location_key="<string>"
obj.time_zone='Europe/Berlin'
```

[Go to Summary](#summary)
## `ListFilesAction` (in `pydag\nodes\documents\ListFilesAction.py`)

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
from pydag.nodes.documents.ListFilesAction import ListFilesAction  # Adjust import if needed

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
## `MoveFilesAction` (in `pydag\nodes\documents\MoveFilesAction.py`)

`Action` that moves files to a new `target_folder`
<br>this `Action` either needs a parent `Node` with a `ListBuffer` with filepaths or a reference to a `Buffer` via `buffer_id` or its `buffer`variable

Raises:
    StatemachineException: if folder does not exist or wrong `Buffer` is provided
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `target_folder` | `str` | `` | target folder to move all the files to in Buffer |


```python
# Example usage of `MoveFilesAction`
from pydag.nodes.documents.MoveFilesAction import MoveFilesAction  # Adjust import if needed

obj = MoveFilesAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.target_folder="path/to/folder"
```

[Go to Summary](#summary)
## `PlotlifyAction` (in `pydag\nodes\documents\PlotlifyAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `plot_path` | `str` | `` | path for plotly html file |
| `data` | `list[dict]` | `'list[dict]()'` | plotly data dictionary with buffer keys for x,y,z data |
| `layout` | `dict` | `'dict()'` | plotly layout dictionary |


```python
# Example usage of `PlotlifyAction`
from pydag.nodes.documents.PlotlifyAction import PlotlifyAction  # Adjust import if needed

obj = PlotlifyAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.plot_path="<string>"
obj.data='list[dict]()'
obj.layout='dict()'
```

[Go to Summary](#summary)
## `ReadCsvAction` (in `pydag\nodes\documents\ReadCsvAction.py`)

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
from pydag.nodes.documents.ReadCsvAction import ReadCsvAction  # Adjust import if needed

obj = ReadCsvAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.file_path="path/to/file.txt"
obj.delimiter=';'
```

[Go to Summary](#summary)
## `ReadExcelRangeAction` (in `pydag\nodes\documents\ReadExcelRangeAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `excel_file` | `str` | `` | path to the excel files to read the range from |
| `worksheet` | `str` | `` | name of the worksheet inside the excel to read from |
| `range` | `str` | `` | address of the range in the worksheet inside the excel to read from |
| `has_header` | `bool` | `False` | specifies whether the first row in range contains header descriptions |


```python
# Example usage of `ReadExcelRangeAction`
from pydag.nodes.documents.ReadExcelRangeAction import ReadExcelRangeAction  # Adjust import if needed

obj = ReadExcelRangeAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.excel_file="path/to/file.txt"
obj.worksheet="<string>"
obj.range="<string>"
obj.has_header=False
```

[Go to Summary](#summary)
## `ReadExcelTableAction` (in `pydag\nodes\documents\ReadExcelTableAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `excel_file` | `str` | `` | path to the excel files to read named table from |
| `table_name` | `str` | `` | name of the table inside the excel to read from |


```python
# Example usage of `ReadExcelTableAction`
from pydag.nodes.documents.ReadExcelTableAction import ReadExcelTableAction  # Adjust import if needed

obj = ReadExcelTableAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.excel_file="path/to/file.txt"
obj.table_name="John Doe"
```

[Go to Summary](#summary)
## `ReadJsonAction` (in `pydag\nodes\documents\ReadJsonAction.py`)

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
from pydag.nodes.documents.ReadJsonAction import ReadJsonAction  # Adjust import if needed

obj = ReadJsonAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.file_path="path/to/file.txt"
obj.json_path="<string>"
```

[Go to Summary](#summary)
## `ReadNpzAction` (in `pydag\nodes\documents\ReadNpzAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `file_path` | `str` | `` | path to the *.npz file to read the data from |


```python
# Example usage of `ReadNpzAction`
from pydag.nodes.documents.ReadNpzAction import ReadNpzAction  # Adjust import if needed

obj = ReadNpzAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.file_path="path/to/file.txt"
```

[Go to Summary](#summary)
## `HttpGetAction` (in `pydag\nodes\http\HttpGetAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `url` | `str` | `` | url for HTTP GET method |
| `headers` | `dict[str]` | `` | headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'} |
| `timeout` | `float` | `10` | timeout for requests |
| `json_path` | `str` | `` | JSONPath specififcation to parse or access the data in buffer |


```python
# Example usage of `HttpGetAction`
from pydag.nodes.http.HttpGetAction import HttpGetAction  # Adjust import if needed

obj = HttpGetAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.url="https://example.com"
obj.headers="<string>"
obj.timeout=10
obj.json_path="<string>"
```

[Go to Summary](#summary)
## `HttpPostAction` (in `pydag\nodes\http\HttpPostAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `url` | `str` | `` |  |
| `headers` | `dict[str]` | `` | headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'} |
| `timeout` | `float` | `10` | timeout for requests |
| `json_path` | `str` | `` | JSONPath specififcation to parse or access the data in buffer |
| `persistent` | `bool` | `False` | specifies whether data is removed from buffer after access |
| `n` | `int` | `1` | specifies the number of samples to remove from buffer, n=0 -> all |


```python
# Example usage of `HttpPostAction`
from pydag.nodes.http.HttpPostAction import HttpPostAction  # Adjust import if needed

obj = HttpPostAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.url="https://example.com"
obj.headers="<string>"
obj.timeout=10
obj.json_path="<string>"
obj.persistent=False
obj.n=1
```

[Go to Summary](#summary)
## `ConfigureElementAction` (in `pydag\nodes\utils\ConfigureElementAction.py`)

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
| `persistent` | `bool` | `True` |  |
| `extract_key` | `str` | `` |  |


```python
# Example usage of `ConfigureElementAction`
from pydag.nodes.utils.ConfigureElementAction import ConfigureElementAction  # Adjust import if needed

obj = ConfigureElementAction()
obj.child_ids='list()'
obj.buffer_id="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.option="<string>"
obj.element_id="<string>"
obj.n=1
obj.persistent=True
obj.extract_key="<string>"
```

[Go to Summary](#summary)
## `CountAction` (in `pydag\nodes\utils\CountAction.py`)

Action that counts the number of times it has been called.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `CountAction`
from pydag.nodes.utils.CountAction import CountAction  # Adjust import if needed

obj = CountAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `CountTransition` (in `pydag\nodes\utils\CountTransition.py`)

A transition that counts the number of times it has been triggered.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `CountTransition`
from pydag.nodes.utils.CountTransition import CountTransition  # Adjust import if needed

obj = CountTransition()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `FalseTransition` (in `pydag\nodes\utils\FalseTransition.py`)

A transition that always returns False.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `FalseTransition`
from pydag.nodes.utils.FalseTransition import FalseTransition  # Adjust import if needed

obj = FalseTransition()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `JoinTransition` (in `pydag\nodes\utils\JoinTransition.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `JoinTransition`
from pydag.nodes.utils.JoinTransition import JoinTransition  # Adjust import if needed

obj = JoinTransition()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `MailAction` (in `pydag\nodes\utils\MailAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `smtp_server` | `str` | `` | host of the mail server to use |
| `port` | `int` | `` | port of the smtp server |
| `mail_account` | `str` | `` | mail account to use for login |
| `pw` | `str` | `` | password of the mail server |
| `recipients` | `list[str]` | `'list[str]()'` | mail address of the recipient |
| `subject` | `str` | `` | subject of the mail |
| `body` | `str` | `` | body of the mail |
| `tls` | `bool` | `True` | use TLS for the connection |


```python
# Example usage of `MailAction`
from pydag.nodes.utils.MailAction import MailAction  # Adjust import if needed

obj = MailAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.smtp_server="<string>"
obj.port=1
obj.mail_account="<string>"
obj.pw="<string>"
obj.recipients='list[str]()'
obj.subject="<string>"
obj.body="<string>"
obj.tls=True
```

[Go to Summary](#summary)
## `PrintAction` (in `pydag\nodes\utils\PrintAction.py`)

An action that prints a message when executed.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `PrintAction`
from pydag.nodes.utils.PrintAction import PrintAction  # Adjust import if needed

obj = PrintAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `SleepAction` (in `pydag\nodes\utils\SleepAction.py`)

An action that sleeps for a specified number of seconds.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `sleep_time` | `int` | `0` | number of seconds to sleep for |


```python
# Example usage of `SleepAction`
from pydag.nodes.utils.SleepAction import SleepAction  # Adjust import if needed

obj = SleepAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.sleep_time=0
```

[Go to Summary](#summary)
## `SleepUntilAction` (in `pydag\nodes\utils\SleepUntilAction.py`)

An action that sleeps until the specified daytime.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `daytime` | `str` | `` | day time when the sleep should end, format hh:mm:ss |


```python
# Example usage of `SleepUntilAction`
from pydag.nodes.utils.SleepUntilAction import SleepUntilAction  # Adjust import if needed

obj = SleepUntilAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.daytime="<string>"
```

[Go to Summary](#summary)
## `StartAction` (in `pydag\nodes\utils\StartAction.py`)

An action that starts the state machine.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `StartAction`
from pydag.nodes.utils.StartAction import StartAction  # Adjust import if needed

obj = StartAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `StopAction` (in `pydag\nodes\utils\StopAction.py`)

An action that stops the state machine.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `StopAction`
from pydag.nodes.utils.StopAction import StopAction  # Adjust import if needed

obj = StopAction()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `TrueTransition` (in `pydag\nodes\utils\TrueTransition.py`)

A transition that always returns True.
This is used to test the statemachine without any conditions.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()'` | List of child node IDs |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `TrueTransition`
from pydag.nodes.utils.TrueTransition import TrueTransition  # Adjust import if needed

obj = TrueTransition()
obj.child_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)