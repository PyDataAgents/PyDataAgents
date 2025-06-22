# Node Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Action`](#action-from-Action) |  |
| [`Adapter`](#adapter-from-Adapter) | Abstract base class for data adapters. |
| [`AdapterNode`](#adapternode-from-AdapterNode) | AdapterNode is a specialized BufferNode that integrates an adapter for data processing. |
| [`BrowserAutomationService`](#browserautomationservice-from-BrowserAutomationService) |  |
| [`Buffer`](#buffer-from-Buffer) | Abstract base class for buffers. |
| [`BufferNode`](#buffernode-from-BufferNode) |  |
| [`DictBuffer`](#dictbuffer-from-DictBuffer) | buffer that stores its values in a dictionary in a table like fashion, where every key contains a list of data |
| [`GrabberNode`](#grabbernode-from-GrabberNode) |  |
| [`JoinTransition`](#jointransition-from-JoinTransition) |  |
| [`LLMService`](#llmservice-from-LLMService) | LLM Service for chat based LLM interaction |
| [`ListBuffer`](#listbuffer-from-ListBuffer) | buffer that stores its values in a capacity limited list |
| [`Mapping`](#mapping-from-Mapping) |  |
| [`MappingNode`](#mappingnode-from-MappingNode) |  |
| [`MappingObserver`](#mappingobserver-from-MappingObserver) | abstract base class for mapping observers |
| [`MappingThread`](#mappingthread-from-MappingThread) |  |
| [`Node`](#node-from-Node) |  |
| [`ObjectTransformation`](#objecttransformation-from-ObjectTransformation) | Abstract base class for object transformations for buffers |
| [`Observer`](#observer-from-Observer) |  |
| [`ObserverThread`](#observerthread-from-ObserverThread) |  |
| [`PlotService`](#plotservice-from-PlotService) |  |
| [`PublishAdapter`](#publishadapter-from-PublishAdapter) | abstract class for Adapter Interface for publishing to data sinks |
| [`PublishMappingObserver`](#publishmappingobserver-from-PublishMappingObserver) |  |
| [`RAGService`](#ragservice-from-RAGService) | Retrieval Augmented Generation (RAG) Service for document based LLM knowledge retrieval in chat form |
| [`ReadAdapter`](#readadapter-from-ReadAdapter) | abstract class for Adapter Interface for reading from data sources |
| [`ReadMappingObserver`](#readmappingobserver-from-ReadMappingObserver) |  |
| [`SampledBuffer`](#sampledbuffer-from-SampledBuffer) | A buffer that samples a signal at a specified interval. |
| [`Service`](#service-from-Service) | abstract base class for Grabber Services |
| [`ServiceNode`](#servicenode-from-ServiceNode) | A class representing a service node in a state machine. |
| [`SignalBuffer`](#signalbuffer-from-SignalBuffer) | A buffer that holds signals with a specific start time and elapsed time. |
| [`StatemachineObserver`](#statemachineobserver-from-StatemachineObserver) | Observer for the StatemachineService. |
| [`StatemachineService`](#statemachineservice-from-StatemachineService) |  |
| [`SubscribeAdapter`](#subscribeadapter-from-SubscribeAdapter) | abstract class for Adapter Interface for subscribing from data sources |
| [`SubscribeMappingObserver`](#subscribemappingobserver-from-SubscribeMappingObserver) |  |
| [`TimedBuffer`](#timedbuffer-from-TimedBuffer) | A buffer that stores data with timestamps. |
| [`TransformsBuffer`](#transformsbuffer-from-TransformsBuffer) | TransformsBuffer is a subclass of ListBuffer that allows for data transformation. |
| [`Transition`](#transition-from-Transition) |  |
| [`WriteAdapter`](#writeadapter-from-WriteAdapter) | abstract class for Adapter Interface for writing to data sinks |
| [`WriteMappingObserver`](#writemappingobserver-from-WriteMappingObserver) |  |
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
| [`AdsAdapter`](#adsadapter-from-ads\AdsAdapter) |  |
| [`AudioAdapter`](#audioadapter-from-audio\AudioAdapter) |  |
| [`CsvReadAdapter`](#csvreadadapter-from-csv\CsvReadAdapter) |  |
| [`CsvWriteAdapter`](#csvwriteadapter-from-csv\CsvWriteAdapter) |  |
| [`HttpAdapter`](#httpadapter-from-http\HttpAdapter) | Adapter for reading and writing data from/to http endpoints |
| [`InfluxDbAdapter`](#influxdbadapter-from-influxdb\InfluxDbAdapter) | InfluxAdapter is a specialized adapter for reading from and writing to InfluxDB. |
| [`MQTTAdapter`](#mqttadapter-from-mqtt\MQTTAdapter) |  |
| [`OpcUaAdapter`](#opcuaadapter-from-opcua\OpcUaAdapter) |  |
| [`ExcelRestService`](#excelrestservice-from-rest\ExcelRestService) | Service for creating a REST API for accessing named Tables in Excel |
| [`LLMRestService`](#llmrestservice-from-rest\LLMRestService) | Service for creating a REST API for accessing LLM Models |
| [`RestService`](#restservice-from-rest\RestService) | Service for creating a REST API for DataGrabber using FastAPI |
| [`S7Adapter`](#s7adapter-from-s7\S7Adapter) | S7Adapter is a specialized adapter for reading from and writing to S7 PLCs. |
| [`SampledSignal`](#sampledsignal-from-signals\SampledSignal) | A class representing a sampled signal for continuously sampled data |
| [`SampledSine`](#sampledsine-from-signals\SampledSine) | A class to represent a sampled sine wave signal. |
| [`Signal`](#signal-from-signals\Signal) | Abstract base class for signals. |
| [`Sine`](#sine-from-signals\Sine) | A class to represent a sine wave signal. |
| [`ByteStreamAdapter`](#bytestreamadapter-from-socket\ByteStreamAdapter) |  |
| [`WebSocketAdapter`](#websocketadapter-from-socket\WebSocketAdapter) |  |
| [`SQLAdapter`](#sqladapter-from-sql\SQLAdapter) |  |
| [`ClippingTransformation`](#clippingtransformation-from-transformations\ClippingTransformation) |  |
| [`BufferInRangeTransition`](#bufferinrangetransition-from-transitions\BufferInRangeTransition) | A transition that compares the current buffer with a target value. |
| [`CompareBufferTransition`](#comparebuffertransition-from-transitions\CompareBufferTransition) | A transition that compares the current buffer with a target value. |
| [`FalseTransition`](#falsetransition-from-transitions\FalseTransition) | A transition that always returns False. |
| [`TrueTransition`](#truetransition-from-transitions\TrueTransition) | A transition that always returns True. |



## `Action` (from `Action.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |


```python
# Example usage of `Action`
from pydatagrabber import Action  # Adjust import if needed

obj = Action(
    child_ids='list()()'
)
```

## `Adapter` (from `Adapter.py`)

Abstract base class for data adapters.
_No fields defined._

## `AdapterNode` (from `AdapterNode.py`)

AdapterNode is a specialized BufferNode that integrates an adapter for data processing.
It inherits from BufferNode to manage buffers and provides methods to interact with the adapter.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `adapter_id` | `str` | `` | ID of the adapter |


```python
# Example usage of `AdapterNode`
from pydatagrabber import AdapterNode  # Adjust import if needed

obj = AdapterNode(
    child_ids='list()()',
    buffer_id="<string>",
    adapter_id="<string>"
)
```

## `BrowserAutomationService` (from `BrowserAutomationService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `browser_type` | `str` | `'EDGE'` | type of browser, EDGE | FIREFOX | CHROME |


```python
# Example usage of `BrowserAutomationService`
from pydatagrabber import BrowserAutomationService  # Adjust import if needed

obj = BrowserAutomationService(
    browser_type='EDGE'
)
```

## `Buffer` (from `Buffer.py`)

Abstract base class for buffers.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |


```python
# Example usage of `Buffer`
from pydatagrabber import Buffer  # Adjust import if needed

obj = Buffer(
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>"
)
```

## `BufferNode` (from `BufferNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |


```python
# Example usage of `BufferNode`
from pydatagrabber import BufferNode  # Adjust import if needed

obj = BufferNode(
    child_ids='list()()',
    buffer_id="<string>"
)
```

## `DictBuffer` (from `DictBuffer.py`)

buffer that stores its values in a dictionary in a table like fashion, where every key contains a list of data
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |


```python
# Example usage of `DictBuffer`
from pydatagrabber import DictBuffer  # Adjust import if needed

obj = DictBuffer(
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>"
)
```

## `GrabberNode` (from `GrabberNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |


```python
# Example usage of `GrabberNode`
from pydatagrabber import GrabberNode  # Adjust import if needed

obj = GrabberNode(
    child_ids='list()()'
)
```

## `JoinTransition` (from `JoinTransition.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |


```python
# Example usage of `JoinTransition`
from pydatagrabber import JoinTransition  # Adjust import if needed

obj = JoinTransition(
    child_ids='list()()'
)
```

## `LLMService` (from `LLMService.py`)

LLM Service for chat based LLM interaction

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `api_key` | `str` | `` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | `` | endpoint of the LLM provider |
| `model_provider` | `str` | `` | name of the model provider, e.g. OPENAI | OLLAMA | ... |
| `model` | `str` | `` | name of the model, e.g. gpt-4o | gemma:1b | ...  |
| `retain_messages` | `bool` | `False` | specify True if you want to retain the chat history for context |


```python
# Example usage of `LLMService`
from pydatagrabber import LLMService  # Adjust import if needed

obj = LLMService(
    api_key="<string>",
    endpoint="<string>",
    model_provider="<string>",
    model="<string>",
    retain_messages=False
)
```

## `ListBuffer` (from `ListBuffer.py`)

buffer that stores its values in a capacity limited list
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |


```python
# Example usage of `ListBuffer`
from pydatagrabber import ListBuffer  # Adjust import if needed

obj = ListBuffer(
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>"
)
```

## `Mapping` (from `Mapping.py`)

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `buffer_ids` | `list[str]` | `` | list of buffer ids to map from |
| `adapter_id` | `str` | `` | id of the Adapter used for this Mapping |
| `addresses` | `list[str]` | `` | list of addresses to read/subscribe from or write/publish to |
| `thread_type` | `str` | `'ThreadType.MILLI_SECOND.value'` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, ... |
| `mapping_type` | `str` | `` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `1` | number of samples to insert or remove from buffers |
| `sampling_period` | `int` | `100` | sampling period to apply in this Mapping |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with grabber start |


```python
# Example usage of `Mapping`
from pydatagrabber import Mapping  # Adjust import if needed

obj = Mapping(
    buffer_ids="<string>",
    adapter_id="<string>",
    addresses="<string>",
    thread_type='ThreadType.MILLI_SECOND.value',
    mapping_type="<string>",
    n=1,
    sampling_period=100,
    persistent=True,
    auto_start=True
)
```

## `MappingNode` (from `MappingNode.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `mapping_id` | `str` | `` | ID of the mapping |


```python
# Example usage of `MappingNode`
from pydatagrabber import MappingNode  # Adjust import if needed

obj = MappingNode(
    child_ids='list()()',
    mapping_id="<string>"
)
```

## `MappingObserver` (from `MappingObserver.py`)

abstract base class for mapping observers
    
_No fields defined._

## `MappingThread` (from `MappingThread.py`)

_No fields defined._

## `Node` (from `Node.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |


```python
# Example usage of `Node`
from pydatagrabber import Node  # Adjust import if needed

obj = Node(
    child_ids='list()()'
)
```

## `ObjectTransformation` (from `ObjectTransformation.py`)

Abstract base class for object transformations for buffers
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `datatype` | `str` | `'DataType.FLOAT.value'` | type of data expected for the transform |


```python
# Example usage of `ObjectTransformation`
from pydatagrabber import ObjectTransformation  # Adjust import if needed

obj = ObjectTransformation(
    datatype='DataType.FLOAT.value'
)
```

## `Observer` (from `Observer.py`)

_No fields defined._

## `ObserverThread` (from `ObserverThread.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `SAFETY_DIFF_TIME_UNITS` | `int` | `` |  |
| `SLEEP_WITH_HOLD_FACTOR` | `float` | `` |  |


```python
# Example usage of `ObserverThread`
from pydatagrabber import ObserverThread  # Adjust import if needed

obj = ObserverThread(
    SAFETY_DIFF_TIME_UNITS=1,
    SLEEP_WITH_HOLD_FACTOR=3.14
)
```

## `PlotService` (from `PlotService.py`)

_No fields defined._

## `PublishAdapter` (from `PublishAdapter.py`)

abstract class for Adapter Interface for publishing to data sinks
    
_No fields defined._

## `PublishMappingObserver` (from `PublishMappingObserver.py`)

_No fields defined._

## `RAGService` (from `RAGService.py`)

Retrieval Augmented Generation (RAG) Service for document based LLM knowledge retrieval in chat form

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `api_key` | `str` | `` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | `` | endpoint of the LLM provider |
| `model_provider` | `str` | `` | name of the model provider, e.g. OPENAI | OLLAMA | ... |
| `model` | `str` | `` | name of the model, e.g. gpt-4o | gemma:1b | ...  |
| `document_links` | `list[str]` | `'list()()'` | list of document links to load into embedded store on startup |
| `retain_messages` | `bool` | `False` | specify True if you want to retain the chat history for context |
| `ignore_invalid_documents` | `bool` | `False` | api token for a web based model provider, e.g. OPENAI |
| `embedding_model` | `str` | `'all-MiniLM-L6-v2'` | name of the embedding model to use for embedding store |
| `persist_directory` | `str` | `` | directory for persisting the embedded store |


```python
# Example usage of `RAGService`
from pydatagrabber import RAGService  # Adjust import if needed

obj = RAGService(
    api_key="<string>",
    endpoint="<string>",
    model_provider="<string>",
    model="<string>",
    document_links='list()()',
    retain_messages=False,
    ignore_invalid_documents=False,
    embedding_model='all-MiniLM-L6-v2',
    persist_directory="<string>"
)
```

## `ReadAdapter` (from `ReadAdapter.py`)

abstract class for Adapter Interface for reading from data sources
    
_No fields defined._

## `ReadMappingObserver` (from `ReadMappingObserver.py`)

_No fields defined._

## `SampledBuffer` (from `SampledBuffer.py`)

A buffer that samples a signal at a specified interval.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |


```python
# Example usage of `SampledBuffer`
from pydatagrabber import SampledBuffer  # Adjust import if needed

obj = SampledBuffer(
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>"
)
```

## `Service` (from `Service.py`)

abstract base class for Grabber Services
    
_No fields defined._

## `ServiceNode` (from `ServiceNode.py`)

A class representing a service node in a state machine.
Inherits from Node and adds functionality specific to service nodes.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service |


```python
# Example usage of `ServiceNode`
from pydatagrabber import ServiceNode  # Adjust import if needed

obj = ServiceNode(
    child_ids='list()()',
    service_id="<string>"
)
```

## `SignalBuffer` (from `SignalBuffer.py`)

A buffer that holds signals with a specific start time and elapsed time.

Attributes:
    start_time (int): The start time of the signal in milliseconds.
    elapsed_time (float): The elapsed time since the start in seconds.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `signal` | `Signal` | `` | a signal object to simulate data |
| `sampling_period` | `int` | `100` | interval in milliseconds for update |


```python
# Example usage of `SignalBuffer`
from pydatagrabber import SignalBuffer  # Adjust import if needed

obj = SignalBuffer(
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>",
    signal="<value>",
    sampling_period=100
)
```

## `StatemachineObserver` (from `StatemachineObserver.py`)

Observer for the StatemachineService.
This observer is be used to start the statemachine in a separate thread
_No fields defined._

## `StatemachineService` (from `StatemachineService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `retry_error_nodes` | `bool` | `False` | Statemachine object containing actions and transitions to go through to represent a state machine program flow |
| `start_node_id` | `str` | `` | ID of the start node in the statemachine service |
| `nodes` | `dict[str, Node]` | `'dict[str, Node]()()'` | dictionary of nodes in the statemachine service |
| `thread_type` | `str` | `'ThreadType.INSTANT.value'` |  |


```python
# Example usage of `StatemachineService`
from pydatagrabber import StatemachineService  # Adjust import if needed

obj = StatemachineService(
    retry_error_nodes=False,
    start_node_id="<string>",
    nodes='dict[str, Node]()()',
    thread_type='ThreadType.INSTANT.value'
)
```

## `SubscribeAdapter` (from `SubscribeAdapter.py`)

abstract class for Adapter Interface for subscribing from data sources
    
_No fields defined._

## `SubscribeMappingObserver` (from `SubscribeMappingObserver.py`)

_No fields defined._

## `TimedBuffer` (from `TimedBuffer.py`)

A buffer that stores data with timestamps.
Inherits from ListBuffer.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |


```python
# Example usage of `TimedBuffer`
from pydatagrabber import TimedBuffer  # Adjust import if needed

obj = TimedBuffer(
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>"
)
```

## `TransformsBuffer` (from `TransformsBuffer.py`)

TransformsBuffer is a subclass of ListBuffer that allows for data transformation.
It is used to transform data from one format to another.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `transformations` | `list[ObjectTransformation]` | `[]` | List of transformations to apply to the data |


```python
# Example usage of `TransformsBuffer`
from pydatagrabber import TransformsBuffer  # Adjust import if needed

obj = TransformsBuffer(
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>",
    transformations=[]
)
```

## `Transition` (from `Transition.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |


```python
# Example usage of `Transition`
from pydatagrabber import Transition  # Adjust import if needed

obj = Transition(
    child_ids='list()()'
)
```

## `WriteAdapter` (from `WriteAdapter.py`)

abstract class for Adapter Interface for writing to data sinks
    
_No fields defined._

## `WriteMappingObserver` (from `WriteMappingObserver.py`)

_No fields defined._

## `AdapterReadAction` (from `actions\AdapterReadAction.py`)

Action to read data from an adapter.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `adapter_id` | `str` | `` | ID of the adapter |
| `address` | `str` | `` | The address to read from the adapter. |
| `n` | `int` | `1` | The number of samples to read. |


```python
# Example usage of `AdapterReadAction`
from pydatagrabber import AdapterReadAction  # Adjust import if needed

obj = AdapterReadAction(
    child_ids='list()()',
    buffer_id="<string>",
    adapter_id="<string>",
    address="<string>",
    n=1
)
```

## `AdapterWriteAction` (from `actions\AdapterWriteAction.py`)

Action to write data with an adapter.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `adapter_id` | `str` | `` | ID of the adapter |
| `address` | `str` | `` | The address to read from the adapter. |
| `n` | `int` | `1` | The number of samples to read. |
| `persistent` | `bool` | `False` | If True, the data will be stored in a persistent buffer. |


```python
# Example usage of `AdapterWriteAction`
from pydatagrabber import AdapterWriteAction  # Adjust import if needed

obj = AdapterWriteAction(
    child_ids='list()()',
    buffer_id="<string>",
    adapter_id="<string>",
    address="<string>",
    n=1,
    persistent=False
)
```

## `AddBufferAction` (from `actions\AddBufferAction.py`)

Action to add a buffer to the grabber node.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `config` | `dict` | `` | Configuration for the buffer to be added. |


```python
# Example usage of `AddBufferAction`
from pydatagrabber import AddBufferAction  # Adjust import if needed

obj = AddBufferAction(
    child_ids='list()()',
    config={}
)
```

## `BrowserAutomationAction` (from `actions\BrowserAutomationAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |


```python
# Example usage of `BrowserAutomationAction`
from pydatagrabber import BrowserAutomationAction  # Adjust import if needed

obj = BrowserAutomationAction(
    child_ids='list()()',
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
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `option` | `str` | `` | option to configure with new value |
| `element_id` | `str` | `` | id of the element to change the option for |
| `n` | `int` | `1` | specifies the number of samples to remove from buffer |


```python
# Example usage of `ConfigureElementAction`
from pydatagrabber import ConfigureElementAction  # Adjust import if needed

obj = ConfigureElementAction(
    child_ids='list()()',
    buffer_id="<string>",
    option="<string>",
    element_id="<string>",
    n=1
)
```

## `CopyFilesAction` (from `actions\CopyFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `target_folder` | `str` | `` | target folder to copy all the files to in Buffer |


```python
# Example usage of `CopyFilesAction`
from pydatagrabber import CopyFilesAction  # Adjust import if needed

obj = CopyFilesAction(
    child_ids='list()()',
    buffer_id="<string>",
    target_folder="path/to/folder"
)
```

## `ListFilesAction` (from `actions\ListFilesAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `folder` | `str` | `` | folder to list the files from into a Buffer |
| `pattern` | `str` | `` | paatern to look for in file names |
| `extension` | `str` | `` | extension to include |
| `newer_than_seconds` | `int` | `` | specifies how old in seconds a file can be to be included |


```python
# Example usage of `ListFilesAction`
from pydatagrabber import ListFilesAction  # Adjust import if needed

obj = ListFilesAction(
    child_ids='list()()',
    buffer_id="<string>",
    folder="path/to/folder",
    pattern="<string>",
    extension="<string>",
    newer_than_seconds=1
)
```

## `MailAction` (from `actions\MailAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
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
    child_ids='list()()',
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
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `target_folder` | `str` | `` | target folder to move all the files to in Buffer |


```python
# Example usage of `MoveFilesAction`
from pydatagrabber import MoveFilesAction  # Adjust import if needed

obj = MoveFilesAction(
    child_ids='list()()',
    buffer_id="<string>",
    target_folder="path/to/folder"
)
```

## `ReadCsvAction` (from `actions\ReadCsvAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `file_path` | `str` | `` | path to the csv file to read the data from |
| `delimiter` | `str` | `';'` | delimiter character(s) for this csv file |


```python
# Example usage of `ReadCsvAction`
from pydatagrabber import ReadCsvAction  # Adjust import if needed

obj = ReadCsvAction(
    child_ids='list()()',
    buffer_id="<string>",
    file_path="path/to/file.txt",
    delimiter=';'
)
```

## `ReadJsonAction` (from `actions\ReadJsonAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `file_path` | `str` | `` | path to the json file to read the data from |
| `json_path` | `str` | `` |  |


```python
# Example usage of `ReadJsonAction`
from pydatagrabber import ReadJsonAction  # Adjust import if needed

obj = ReadJsonAction(
    child_ids='list()()',
    buffer_id="<string>",
    file_path="path/to/file.txt",
    json_path="<string>"
)
```

## `SetElementAction` (from `actions\SetElementAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `xpath` | `str` | `` | XPath definition to locate the element to set a value to |


```python
# Example usage of `SetElementAction`
from pydatagrabber import SetElementAction  # Adjust import if needed

obj = SetElementAction(
    child_ids='list()()',
    service_id="<string>",
    buffer_id="<string>",
    xpath="<string>"
)
```

## `SleepAction` (from `actions\SleepAction.py`)

An action that sleeps for a specified number of seconds.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |


```python
# Example usage of `SleepAction`
from pydatagrabber import SleepAction  # Adjust import if needed

obj = SleepAction(
    child_ids='list()()'
)
```

## `StartAction` (from `actions\StartAction.py`)

An action that starts the state machine.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |


```python
# Example usage of `StartAction`
from pydatagrabber import StartAction  # Adjust import if needed

obj = StartAction(
    child_ids='list()()'
)
```

## `StopAction` (from `actions\StopAction.py`)

An action that stops the state machine.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |


```python
# Example usage of `StopAction`
from pydatagrabber import StopAction  # Adjust import if needed

obj = StopAction(
    child_ids='list()()'
)
```

## `UrlNavigateAction` (from `actions\UrlNavigateAction.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `service_id` | `str` | `` | ID of the service to reference for Browser Automation |
| `url` | `str` | `` | url to navigate to in browser |


```python
# Example usage of `UrlNavigateAction`
from pydatagrabber import UrlNavigateAction  # Adjust import if needed

obj = UrlNavigateAction(
    child_ids='list()()',
    service_id="<string>",
    url="https://example.com"
)
```

## `AdsAdapter` (from `ads\AdsAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `ams_net_id` | `str` | `` | AMS Net Id to connect to for ADS Connection |
| `twincat` | `int` | `3` | Twincat version to use, e.g. 2 or 3 for TwinCAT 2/3 |


```python
# Example usage of `AdsAdapter`
from pydatagrabber import AdsAdapter  # Adjust import if needed

obj = AdsAdapter(
    ams_net_id="<string>",
    twincat=3
)
```

## `AudioAdapter` (from `audio\AudioAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sample_rate` | `int` | `44100` | sample rate of audio channel, usually 44100 Hz |
| `device` | `int` | `` | device number to use as input stream, if nothing is specified the default device is used |


```python
# Example usage of `AudioAdapter`
from pydatagrabber import AudioAdapter  # Adjust import if needed

obj = AudioAdapter(
    sample_rate=44100,
    device=1
)
```

## `CsvReadAdapter` (from `csv\CsvReadAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `file_path` | `str` | `` | path to the csv file to read |
| `all_at_once` | `bool` | `True` | read all data at once |
| `delimiter` | `str` | `';'` | delimiter to use to separate columns |
| `has_header` | `bool` | `True` | specifies whether a header is present in data |
| `auto_detect` | `bool` | `False` | specifies whether to use the csv sniffing option |
| `force_numeric` | `bool` | `True` | forces numeric parsing of data |


```python
# Example usage of `CsvReadAdapter`
from pydatagrabber import CsvReadAdapter  # Adjust import if needed

obj = CsvReadAdapter(
    file_path="path/to/file.txt",
    all_at_once=True,
    delimiter=';',
    has_header=True,
    auto_detect=False,
    force_numeric=True
)
```

## `CsvWriteAdapter` (from `csv\CsvWriteAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `folder` | `str` | `` | folder to save the csv files to |
| `file_post_fix` | `str` | `` | postfix to use with every file |
| `file_extension` | `str` | `'csv'` | extension of the files being created, specify without *.*, e.g. 'csv' or 'txt' |
| `with_timestamp` | `bool` | `False` | specify whether the current timestamp in UTC ms should be printed as column |
| `max_samples` | `int` | `1000000` | maximum number of samples in one file, if limit is reached a new file is being created |
| `delimiter` | `str` | `';'` | delimiter to use for column separation |
| `decimal_precision` | `int` | `3` | maximum decimal precision of numeric values |


```python
# Example usage of `CsvWriteAdapter`
from pydatagrabber import CsvWriteAdapter  # Adjust import if needed

obj = CsvWriteAdapter(
    folder="path/to/folder",
    file_post_fix="path/to/file.txt",
    file_extension='csv',
    with_timestamp=False,
    max_samples=1000000,
    delimiter=';',
    decimal_precision=3
)
```

## `HttpAdapter` (from `http\HttpAdapter.py`)

Adapter for reading and writing data from/to http endpoints
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `base_url` | `str` | `` | base URL for the HTTP requests, e.g. http://localhost:8080/api |
| `headers` | `dict[str]` | `` | headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'} |
| `json_path` | `bool` | `False` | if True, the response data is expected to be in JSON format and will be parsed accordingly to specification in address |


```python
# Example usage of `HttpAdapter`
from pydatagrabber import HttpAdapter  # Adjust import if needed

obj = HttpAdapter(
    base_url="https://example.com",
    headers="<string>",
    json_path=False
)
```

## `InfluxDbAdapter` (from `influxdb\InfluxDbAdapter.py`)

InfluxAdapter is a specialized adapter for reading from and writing to InfluxDB.
It inherits from ReadAdapter and WriteAdapter to provide both functionalities.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `endpoint` | `str` | `'http://localhost:8086'` | The endpoint URL for the InfluxDB instance. |
| `token` | `str` | `` | The authentication token for InfluxDB. |
| `org` | `str` | `'my-org'` | The organization name in InfluxDB. |


```python
# Example usage of `InfluxDbAdapter`
from pydatagrabber import InfluxDbAdapter  # Adjust import if needed

obj = InfluxDbAdapter(
    endpoint='http://localhost:8086',
    token="<string>",
    org='my-org'
)
```

## `MQTTAdapter` (from `mqtt\MQTTAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `endpoint` | `str` | `` | endpoint of the MQTT broker, e.g. test.mosquitto.org (public test broker) |
| `port` | `int` | `1883` | port of the mqtt broker |
| `keep_alive` | `int` | `60` | keep alive interval with broker |
| `force_numeric` | `bool` | `False` | specifies if the payload from mqtt topics should be parsed as numeric value, rather than string |
| `retain` | `bool` | `False` | specifies whether messages should be retained on publishing |
| `qos` | `int` | `0` | quality of service parameter of mqtt publish |


```python
# Example usage of `MQTTAdapter`
from pydatagrabber import MQTTAdapter  # Adjust import if needed

obj = MQTTAdapter(
    endpoint="<string>",
    port=1883,
    keep_alive=60,
    force_numeric=False,
    retain=False,
    qos=0
)
```

## `OpcUaAdapter` (from `opcua\OpcUaAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `endpoint` | `str` | `` | endpoint of the opc ua server, e.g. opc.tcp://localhost:48010 |


```python
# Example usage of `OpcUaAdapter`
from pydatagrabber import OpcUaAdapter  # Adjust import if needed

obj = OpcUaAdapter(
    endpoint="<string>"
)
```

## `ExcelRestService` (from `rest\ExcelRestService.py`)

Service for creating a REST API for accessing named Tables in Excel
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `port` | `int` | `8001` | port of the REST API endpoint |
| `excel_file` | `str` | `` | path of the excel file to open for tables |


```python
# Example usage of `ExcelRestService`
from pydatagrabber import ExcelRestService  # Adjust import if needed

obj = ExcelRestService(
    port=8001,
    excel_file="path/to/file.txt"
)
```

## `LLMRestService` (from `rest\LLMRestService.py`)

Service for creating a REST API for accessing LLM Models
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `port` | `int` | `8001` | port of the REST API endpoint |


```python
# Example usage of `LLMRestService`
from pydatagrabber import LLMRestService  # Adjust import if needed

obj = LLMRestService(
    port=8001
)
```

## `RestService` (from `rest\RestService.py`)

Service for creating a REST API for DataGrabber using FastAPI
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `port` | `int` | `8001` | port of the REST API endpoint |


```python
# Example usage of `RestService`
from pydatagrabber import RestService  # Adjust import if needed

obj = RestService(
    port=8001
)
```

## `S7Adapter` (from `s7\S7Adapter.py`)

S7Adapter is a specialized adapter for reading from and writing to S7 PLCs.
It inherits from ReadAdapter and WriteAdapter to provide both functionalities.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `host` | `str` | `'127.0.0.1'` | The IP address or hostname of the S7 PLC. |
| `rack` | `int` | `0` | The rack number of the S7 PLC. |
| `slot` | `int` | `1` | The slot number of the S7 PLC. |


```python
# Example usage of `S7Adapter`
from pydatagrabber import S7Adapter  # Adjust import if needed

obj = S7Adapter(
    host='127.0.0.1',
    rack=0,
    slot=1
)
```

## `SampledSignal` (from `signals\SampledSignal.py`)

A class representing a sampled signal for continuously sampled data
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sample_rate` | `float` | `1.0` | sample rate of the signal in Hz |


```python
# Example usage of `SampledSignal`
from pydatagrabber import SampledSignal  # Adjust import if needed

obj = SampledSignal(
    sample_rate=1.0
)
```

## `SampledSine` (from `signals\SampledSine.py`)

A class to represent a sampled sine wave signal.

Attributes:
    f (float): The frequency of the sine wave in Hz.
    a (float): The amplitude of the sine wave.
    sample_rate (int): The number of samples per second.
    p (float): The phase of the sine wave in °.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sample_rate` | `float` | `1.0` | sample rate of the signal in Hz |
| `f` | `float` | `1.0` | frequency of sine wave in Hz |
| `a` | `float` | `1.0` | amplitude of sine wave |
| `p` | `float` | `0.0` | phase angle of sine wave in ° |
| `n` | `float` | `0.0` | noise level of sine wave in respect to ampltidue [0..1] |


```python
# Example usage of `SampledSine`
from pydatagrabber import SampledSine  # Adjust import if needed

obj = SampledSine(
    sample_rate=1.0,
    f=1.0,
    a=1.0,
    p=0.0,
    n=0.0
)
```

## `Signal` (from `signals\Signal.py`)

Abstract base class for signals.
_No fields defined._

## `Sine` (from `signals\Sine.py`)

A class to represent a sine wave signal.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `f` | `float` | `1.0` | frequency of sine wave in Hz |
| `a` | `float` | `1.0` | amplitude of sine wave |
| `p` | `float` | `0.0` | phase angle of sine wave in ° |
| `n` | `float` | `0.0` | noise level of sine wave in respect to ampltidue [0..1] |


```python
# Example usage of `Sine`
from pydatagrabber import Sine  # Adjust import if needed

obj = Sine(
    f=1.0,
    a=1.0,
    p=0.0,
    n=0.0
)
```

## `ByteStreamAdapter` (from `socket\ByteStreamAdapter.py`)

_No fields defined._

## `WebSocketAdapter` (from `socket\WebSocketAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | `str` | `` | socket url, e.g. wss://localhost:10001 |


```python
# Example usage of `WebSocketAdapter`
from pydatagrabber import WebSocketAdapter  # Adjust import if needed

obj = WebSocketAdapter(
    url="https://example.com"
)
```

## `SQLAdapter` (from `sql\SQLAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `connection_str` | `str` | `` | connection string for the specific SQL database |


```python
# Example usage of `SQLAdapter`
from pydatagrabber import SQLAdapter  # Adjust import if needed

obj = SQLAdapter(
    connection_str="<string>"
)
```

## `ClippingTransformation` (from `transformations\ClippingTransformation.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `datatype` | `str` | `'DataType.FLOAT.value'` | type of data expected for the transform |
| `lower_limit` | `float` | `0.0` | lower limit for clipping |
| `upper_limit` | `float` | `1.0` | upper limit for clipping |


```python
# Example usage of `ClippingTransformation`
from pydatagrabber import ClippingTransformation  # Adjust import if needed

obj = ClippingTransformation(
    datatype='DataType.FLOAT.value',
    lower_limit=0.0,
    upper_limit=1.0
)
```

## `BufferInRangeTransition` (from `transitions\BufferInRangeTransition.py`)

A transition that compares the current buffer with a target value.
If the buffer matches the target, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `comparator` | `str` | `` | The comparison operator to use. |
| `value` | `any` | `` | The value to compare against the buffer. |


```python
# Example usage of `BufferInRangeTransition`
from pydatagrabber import BufferInRangeTransition  # Adjust import if needed

obj = BufferInRangeTransition(
    child_ids='list()()',
    buffer_id="<string>",
    comparator="<string>",
    value="<value>"
)
```

## `CompareBufferTransition` (from `transitions\CompareBufferTransition.py`)

A transition that compares the current buffer with a target value.
If the buffer matches the target, the transition is successful.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |
| `buffer_id` | `str` | `` | unique ID of the buffer |
| `comparator` | `str` | `` | The comparison operator to use. |
| `value` | `any` | `` | The value to compare against the buffer. |


```python
# Example usage of `CompareBufferTransition`
from pydatagrabber import CompareBufferTransition  # Adjust import if needed

obj = CompareBufferTransition(
    child_ids='list()()',
    buffer_id="<string>",
    comparator="<string>",
    value="<value>"
)
```

## `FalseTransition` (from `transitions\FalseTransition.py`)

A transition that always returns False.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |


```python
# Example usage of `FalseTransition`
from pydatagrabber import FalseTransition  # Adjust import if needed

obj = FalseTransition(
    child_ids='list()()'
)
```

## `TrueTransition` (from `transitions\TrueTransition.py`)

A transition that always returns True.
This is used to test the statemachine without any conditions.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `child_ids` | `list[str]` | `'list()()'` | List of child node IDs |


```python
# Example usage of `TrueTransition`
from pydatagrabber import TrueTransition  # Adjust import if needed

obj = TrueTransition(
    child_ids='list()()'
)
```
