# Grabber Elements Documentation

## `Adapter` (from `adapters\Adapter.py`)

_No fields defined._

## `PublishAdapter` (from `adapters\PublishAdapter.py`)

_No fields defined._

## `ReadAdapter` (from `adapters\ReadAdapter.py`)

_No fields defined._

## `SubscribeAdapter` (from `adapters\SubscribeAdapter.py`)

_No fields defined._

## `WriteAdapter` (from `adapters\WriteAdapter.py`)

_No fields defined._

## `AdsAdapter` (from `adapters\ads\AdsAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `ams_net_id` | `str` | AMS Net Id to connect to for ADS Connection |
| `twincat` | `int` | Twincat version to use, e.g. 2 or 3 for TwinCAT 2/3 |

## `AudioAdapter` (from `adapters\audio\AudioAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `sample_rate` | `int` | sample rate of audio channel, usually 44100 Hz |
| `device` | `int` | device number to use as input stream, if nothing is specified the default device is used |

## `CsvReadAdapter` (from `adapters\csv\CsvReadAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | path to the csv file to read |
| `all_at_once` | `bool` | read all data at once |
| `delimiter` | `str` | delimiter to use to separate columns |
| `has_header` | `bool` | specifies whether a header is present in data |
| `auto_detect` | `bool` | specifies whether to use the csv sniffing option |
| `force_numeric` | `bool` | forces numeric parsing of data |

## `CsvWriteAdapter` (from `adapters\csv\CsvWriteAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `folder` | `str` | folder to save the csv files to |
| `file_post_fix` | `str` | postfix to use with every file |
| `file_extension` | `str` | extension of the files being created, specify without *.*, e.g. 'csv' or 'txt' |
| `with_timestamp` | `bool` | specify whether the current timestamp in UTC ms should be printed as column |
| `max_samples` | `int` | maximum number of samples in one file, if limit is reached a new file is being created |
| `delimiter` | `str` | delimiter to use for column separation |
| `decimal_precision` | `int` | maximum decimal precision of numeric values |

## `HttpAdapter` (from `adapters\http\HttpAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `base_url` | `str` | base URL for the HTTP requests, e.g. http://localhost:8080/api |
| `headers` | `dict[str]` | headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'} |
| `json_path` | `bool` | if True, the response data is expected to be in JSON format and will be parsed accordingly to specification in address |

## `InfluxDbAdapter` (from `adapters\influxdb\InfluxDbAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `endpoint` | `str` | The endpoint URL for the InfluxDB instance. |
| `token` | `str` | The authentication token for InfluxDB. |
| `org` | `str` | The organization name in InfluxDB. |

## `MQTTAdapter` (from `adapters\mqtt\MQTTAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `endpoint` | `str` | endpoint of the MQTT broker, e.g. test.mosquitto.org (public test broker) |
| `port` | `int` | port of the mqtt broker |
| `keep_alive` | `int` | keep alive interval with broker |
| `force_numeric` | `bool` | specifies if the payload from mqtt topics should be parsed as numeric value, rather than string |
| `retain` | `bool` | specifies whether messages should be retained on publishing |
| `qos` | `int` | quality of service parameter of mqtt publish |

## `OpcUaAdapter` (from `adapters\opcua\OpcUaAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `endpoint` | `str` | endpoint of the opc ua server, e.g. opc.tcp://localhost:48010 |

## `S7Adapter` (from `adapters\s7\S7Adapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `host` | `str` | The IP address or hostname of the S7 PLC. |
| `rack` | `int` | The rack number of the S7 PLC. |
| `slot` | `int` | The slot number of the S7 PLC. |

## `ByteStreamAdapter` (from `adapters\socket\ByteStreamAdapter.py`)

_No fields defined._

## `WebSocketAdapter` (from `adapters\socket\WebSocketAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `url` | `str` | socket url, e.g. wss://localhost:10001 |

## `SQLAdapter` (from `adapters\sql\SQLAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `connection_str` | `str` | connection string for the specific SQL database |

## `Buffer` (from `buffers\Buffer.py`)

| Field | Type | Description |
|-------|------|-------------|
| `capacity` | `int` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | initial values in buffer |
| `unit` | `any` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | buffer description |

## `DictBuffer` (from `buffers\DictBuffer.py`)

_No fields defined._

## `ListBuffer` (from `buffers\ListBuffer.py`)

_No fields defined._

## `ObjectTransformation` (from `buffers\ObjectTransformation.py`)

| Field | Type | Description |
|-------|------|-------------|
| `datatype` | `str` | type of data expected for the transform |

## `SampledBuffer` (from `buffers\SampledBuffer.py`)

_No fields defined._

## `SignalBuffer` (from `buffers\SignalBuffer.py`)

| Field | Type | Description |
|-------|------|-------------|
| `signal` | `Signal` | a signal object to simulate data |
| `sampling_period` | `int` | interval in milliseconds for update |

## `TimedBuffer` (from `buffers\TimedBuffer.py`)

_No fields defined._

## `TransformsBuffer` (from `buffers\TransformsBuffer.py`)

| Field | Type | Description |
|-------|------|-------------|
| `transformations` | `list[ObjectTransformation]` | List of transformations to apply to the data |

## `SampledSignal` (from `buffers\signals\SampledSignal.py`)

| Field | Type | Description |
|-------|------|-------------|
| `sample_rate` | `float` | sample rate of the signal in Hz |

## `SampledSine` (from `buffers\signals\SampledSine.py`)

| Field | Type | Description |
|-------|------|-------------|
| `f` | `float` | frequency of sine wave in Hz |
| `a` | `float` | amplitude of sine wave |
| `p` | `float` | phase angle of sine wave in ° |
| `n` | `float` | noise level of sine wave in respect to ampltidue [0..1] |

## `Signal` (from `buffers\signals\Signal.py`)

_No fields defined._

## `Sine` (from `buffers\signals\Sine.py`)

| Field | Type | Description |
|-------|------|-------------|
| `f` | `float` | frequency of sine wave in Hz |
| `a` | `float` | amplitude of sine wave |
| `p` | `float` | phase angle of sine wave in ° |
| `n` | `float` | noise level of sine wave in respect to ampltidue [0..1] |

## `ClippingTransformation` (from `buffers\transformations\ClippingTransformation.py`)

| Field | Type | Description |
|-------|------|-------------|
| `lower_limit` | `float` | lower limit for clipping |
| `upper_limit` | `float` | upper limit for clipping |

## `Grabber` (from `grabbers\Grabber.py`)

_No fields defined._

## `Mapping` (from `mappings\Mapping.py`)

| Field | Type | Description |
|-------|------|-------------|
| `buffer_ids` | `list[str]` | list of buffer ids to map from |
| `adapter_id` | `str` | id of the Adapter used for this Mapping |
| `addresses` | `list[str]` | list of addresses to read/subscribe from or write/publish to |
| `thread_type` | `str` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, ... |
| `mapping_type` | `str` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | number of samples to insert or remove from buffers |
| `sampling_period` | `int` | sampling period to apply in this Mapping |
| `persistent` | `bool` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `auto_start` | `bool` | specifies whether to start the mapping with grabber start |

## `MappingObserver` (from `mappings\MappingObserver.py`)

_No fields defined._

## `MappingThread` (from `mappings\MappingThread.py`)

_No fields defined._

## `Observer` (from `mappings\Observer.py`)

_No fields defined._

## `ObserverThread` (from `mappings\ObserverThread.py`)

| Field | Type | Description |
|-------|------|-------------|
| `SAFETY_DIFF_TIME_UNITS` | `int` |  |
| `SLEEP_WITH_HOLD_FACTOR` | `float` |  |

## `PublishMappingObserver` (from `mappings\PublishMappingObserver.py`)

_No fields defined._

## `ReadMappingObserver` (from `mappings\ReadMappingObserver.py`)

_No fields defined._

## `SubscribeMappingObserver` (from `mappings\SubscribeMappingObserver.py`)

_No fields defined._

## `WriteMappingObserver` (from `mappings\WriteMappingObserver.py`)

_No fields defined._

## `BrowserAutomationService` (from `services\BrowserAutomationService.py`)

| Field | Type | Description |
|-------|------|-------------|
| `browser_type` | `str` | type of browser, EDGE | FIREFOX | CHROME |

## `LLMService` (from `services\LLMService.py`)

| Field | Type | Description |
|-------|------|-------------|
| `api_key` | `str` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | endpoint of the LLM provider |
| `model_provider` | `str` | name of the model provider, e.g. OPENAI | OLLAMA | ... |
| `model` | `str` | name of the model, e.g. gpt-4o | gemma:1b | ...  |
| `retain_messages` | `bool` | specify True if you want to retain the chat history for context |

## `PlotService` (from `services\PlotService.py`)

_No fields defined._

## `RAGService` (from `services\RAGService.py`)

| Field | Type | Description |
|-------|------|-------------|
| `api_key` | `str` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | endpoint of the LLM provider |
| `model_provider` | `str` | name of the model provider, e.g. OPENAI | OLLAMA | ... |
| `model` | `str` | name of the model, e.g. gpt-4o | gemma:1b | ...  |
| `document_links` | `list[str]` | list of document links to load into embedded store on startup |
| `retain_messages` | `bool` | specify True if you want to retain the chat history for context |
| `ignore_invalid_documents` | `bool` | api token for a web based model provider, e.g. OPENAI |
| `embedding_model` | `str` | name of the embedding model to use for embedding store |
| `persist_directory` | `str` | directory for persisting the embedded store |

## `Service` (from `services\Service.py`)

_No fields defined._

## `ExcelRestService` (from `services\rest\ExcelRestService.py`)

| Field | Type | Description |
|-------|------|-------------|
| `excel_file` | `str` | path of the excel file to open for tables |

## `LLMRestService` (from `services\rest\LLMRestService.py`)

_No fields defined._

## `RestService` (from `services\rest\RestService.py`)

| Field | Type | Description |
|-------|------|-------------|
| `port` | `int` | port of the REST API endpoint |

## `Action` (from `statemachine\Action.py`)

_No fields defined._

## `AdapterNode` (from `statemachine\AdapterNode.py`)

| Field | Type | Description |
|-------|------|-------------|
| `adapter_id` | `str` | ID of the adapter |

## `BufferNode` (from `statemachine\BufferNode.py`)

| Field | Type | Description |
|-------|------|-------------|
| `buffer_id` | `str` | unique ID of the buffer |

## `GrabberNode` (from `statemachine\GrabberNode.py`)

_No fields defined._

## `JoinTransition` (from `statemachine\JoinTransition.py`)

_No fields defined._

## `MappingNode` (from `statemachine\MappingNode.py`)

| Field | Type | Description |
|-------|------|-------------|
| `mapping_id` | `str` | ID of the mapping |

## `Node` (from `statemachine\Node.py`)

| Field | Type | Description |
|-------|------|-------------|
| `child_ids` | `list[str]` | List of child node IDs |

## `ServiceNode` (from `statemachine\ServiceNode.py`)

| Field | Type | Description |
|-------|------|-------------|
| `service_id` | `str` | ID of the service |

## `StatemachineObserver` (from `statemachine\StatemachineObserver.py`)

_No fields defined._

## `StatemachineService` (from `statemachine\StatemachineService.py`)

| Field | Type | Description |
|-------|------|-------------|
| `retry_error_nodes` | `bool` | Statemachine object containing actions and transitions to go through to represent a state machine program flow |
| `start_node_id` | `str` | ID of the start node in the statemachine service |
| `nodes` | `dict[str, Node]` | dictionary of nodes in the statemachine service |
| `thread_type` | `str` |  |

## `Transition` (from `statemachine\Transition.py`)

_No fields defined._

## `AdapterReadAction` (from `statemachine\actions\AdapterReadAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `address` | `str` | The address to read from the adapter. |
| `n` | `int` | The number of samples to read. |

## `AdapterWriteAction` (from `statemachine\actions\AdapterWriteAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `address` | `str` | The address to read from the adapter. |
| `n` | `int` | The number of samples to read. |
| `persistent` | `bool` | If True, the data will be stored in a persistent buffer. |

## `AddBufferAction` (from `statemachine\actions\AddBufferAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `config` | `dict` | Configuration for the buffer to be added. |

## `BrowserAutomationAction` (from `statemachine\actions\BrowserAutomationAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `service_id` | `str` | ID of the service to reference for Browser Automation |

## `ConfigureElementAction` (from `statemachine\actions\ConfigureElementAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `option` | `str` | option to configure with new value |
| `element_id` | `str` | id of the element to change the option for |
| `n` | `int` | specifies the number of samples to remove from buffer |

## `CopyFilesAction` (from `statemachine\actions\CopyFilesAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `target_folder` | `str` | target folder to copy all the files to in Buffer |

## `ListFilesAction` (from `statemachine\actions\ListFilesAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `folder` | `str` | folder to list the files from into a Buffer |
| `pattern` | `str` | paatern to look for in file names |
| `extension` | `str` | extension to include |
| `newer_than_seconds` | `int` | specifies how old in seconds a file can be to be included |

## `MailAction` (from `statemachine\actions\MailAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `smtp_server` | `str` | host of the mail server to use |
| `port` | `int` | port of the smtp server |
| `mail_account` | `str` | mail account to use for login |
| `pw` | `str` | password of the mail server |
| `recipient` | `str` | mail address of the recipient |
| `subject` | `str` | subject of the mail |
| `body` | `str` | body of the mail |

## `MoveFilesAction` (from `statemachine\actions\MoveFilesAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `target_folder` | `str` | target folder to move all the files to in Buffer |

## `ReadCsvAction` (from `statemachine\actions\ReadCsvAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | path to the csv file to read the data from |
| `delimiter` | `str` | delimiter character(s) for this csv file |

## `ReadJsonAction` (from `statemachine\actions\ReadJsonAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | path to the json file to read the data from |
| `json_path` | `str` |  |

## `SetElementAction` (from `statemachine\actions\SetElementAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `xpath` | `str` | XPath definition to locate the element to set a value to |

## `SleepAction` (from `statemachine\actions\SleepAction.py`)

_No fields defined._

## `StartAction` (from `statemachine\actions\StartAction.py`)

_No fields defined._

## `StopAction` (from `statemachine\actions\StopAction.py`)

_No fields defined._

## `UrlNavigateAction` (from `statemachine\actions\UrlNavigateAction.py`)

| Field | Type | Description |
|-------|------|-------------|
| `url` | `str` | url to navigate to in browser |

## `BufferInRangeTransition` (from `statemachine\transitions\BufferInRangeTransition.py`)

| Field | Type | Description |
|-------|------|-------------|
| `comparator` | `str` | The comparison operator to use. |
| `value` | `any` | The value to compare against the buffer. |

## `CompareBufferTransition` (from `statemachine\transitions\CompareBufferTransition.py`)

| Field | Type | Description |
|-------|------|-------------|
| `comparator` | `str` | The comparison operator to use. |
| `value` | `any` | The value to compare against the buffer. |

## `FalseTransition` (from `statemachine\transitions\FalseTransition.py`)

_No fields defined._

## `TrueTransition` (from `statemachine\transitions\TrueTransition.py`)

_No fields defined._
