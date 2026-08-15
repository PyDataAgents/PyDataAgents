# Services Documentation

## Summary

| Class | Description | Icon |
|-------|-------------|------|
| [`BrowsingService`](#browsingservice-in-pydagservicesbrowsingservicepy) | `ObserverService` Interface for discovering available data sources and their addresses.<br>new `Services` that allow for discovery of sources and addresses must inherit this class. | ![BrowsingService](element_icons/BrowsingService.png)
| [`DiscoveryService`](#discoveryservice-in-pydagservicesdiscoveryservicepy) | `Service` Interface for discovering available data sources and their addresses.   <br>new `Service` that allow for discovery of sources and addresses must inherit this class next to `Service`.Args:    ObserverService (_type_): parent class for all Service, provides basic connection management and state handling | ![DiscoveryService](element_icons/DiscoveryService.png)
| [`MappingService`](#mappingservice-in-pydagservicesmappingservicepy) | A `ObserverService` for mapping `Buffer`s together for reading, writing, subscribing or publishing from sources and sinksRaises:    ServiceException: _description_Returns:    _type_: _description_ | ![MappingService](element_icons/MappingService.png)
| [`ObserverService`](#observerservice-in-pydagservicesobserverservicepy) | abstract base class for Services with ObserverThreads     | ![ObserverService](element_icons/ObserverService.png)
| [`PublishService`](#publishservice-in-pydagservicespublishservicepy) |  | ![PublishService](element_icons/PublishService.png)
| [`ReadService`](#readservice-in-pydagservicesreadservicepy) |  | ![ReadService](element_icons/ReadService.png)
| [`Service`](#service-in-pydagservicesservicepy) | abstract base class for agent Services     | ![Service](element_icons/Service.png)
| [`SubscribeService`](#subscribeservice-in-pydagservicessubscribeservicepy) |  | ![SubscribeService](element_icons/SubscribeService.png)
| [`WriteService`](#writeservice-in-pydagserviceswriteservicepy) |  | ![WriteService](element_icons/WriteService.png)
| [`AdsService`](#adsservice-in-pydagservicesadsadsservicepy) | `MappingService` for reading and writing data from/to Beckhoff TwinCAT PLCs via ADS (Automation Device Specification).     | ![AdsService](element_icons/AdsService.png)
| [`AudioService`](#audioservice-in-pydagservicesaudioaudioservicepy) | `SubscribeService` for subscribing to a system's audio input channels (e.g. from a USB microphone) using the `sounddevice` library.     | ![AudioService](element_icons/AudioService.png)
| [`SolidPDMService`](#solidpdmservice-in-pydagservicescadsolidpdmservicepy) | `Service` for high-level wrapping of SolidWorks PDM Professional COM API.Wraps common vault, file, search, and workflow operations.for help goto:- https://help.solidworks.com/2023/english/api/epdmapi/Welcome-epdmapi.html?utm_source=chatgpt.com- https://github.com/BlueByteSystemsInc/SOLIDWORKS-PDM-API-SDK?utm_source=chatgpt.com- https://www.codestack.net/ | ![SolidPDMService](element_icons/SolidPDMService.png)
| [`SolidWorksService`](#solidworksservice-in-pydagservicescadsolidworksservicepy) |  | ![SolidWorksService](element_icons/SolidWorksService.png)
| [`CsvReadService`](#csvreadservice-in-pydagservicescsvcsvreadservicepy) | `MappingService` for reading data from CSV files.     | ![CsvReadService](element_icons/CsvReadService.png)
| [`CsvWriteService`](#csvwriteservice-in-pydagservicescsvcsvwriteservicepy) | `WriteService` for writing data to CSV files.     | ![CsvWriteService](element_icons/CsvWriteService.png)
| [`DataModelService`](#datamodelservice-in-pydagservicesdatamodeldatamodelservicepy) | `Service` that enables modeling of data, in terms of script based computations on complex data relationships (e.g. to model machine elements or similar)<br>Model execution / model handlerthis file aggregates a chain of method calls, depending on the dependencies of the methods on dataclass variables.This means that only those methods are executed whose variables have changed.The model handler also registers variable inputs (from outside) and method outputs and then initiates the execution of methods accordingly.<br><br>Example of a model file:```pythonimport pandas as pdfrom pydag.services.datamodel.DataModel import DataModel@dataclassclass SimpleDataModel(DataModel):    a : float = field(default=None, metadata={"description": "variable 1"})    b : float = field(default=None, metadata={"description": "variable 2"})    c : float = field(default=None, metadata={"description": "variable 3", "hidden": True})    t : str = field(default=None, metadata={"description": "text variable 1", "hidden": True})    def method1(self):        self.b = self.a * 2 + 10.0        self.c = self.a + self.c        def method2(self):        self.t = f"Hello World {self.c}"        def method3(self, dms : DataModelService):        df = dms.lookup_table('NAME_OF_TABLE')        values = df.query(f"COL1 > 30 and COL2 <= {self.a}")        self.value = values["COL1"].to_list()[0]    ```<br>The model files always have to inherit from `DataModel`, they are `dataclasses` and all properties should be introduced as `fields`.<br><br>As an additional argument to `DataModel` methods the argument `dms` of type `DataModelService` can be passed, which allows acces to the lookup-tables via dms.lookup_store([Name of the table]) with Pandas Dataframes can be provided in order to lookup values based on model variables | ![DataModelService](element_icons/DataModelService.png)
| [`MultiModelService`](#multimodelservice-in-pydagservicesdatamodelmultimodelservicepy) | `Service` that allows the management of multiple `Datamodel`s at once, enhancing the `DataModelService` capabilities     | ![MultiModelService](element_icons/MultiModelService.png)
| [`InfluxDbService`](#influxdbservice-in-pydagservicesdbinfluxdbservicepy) | `MappingService` thats reads or writes to InfluxDB.<br>Address Schema:<br>address = "b=[bucket];m=[measurement];f=[field]" | ![InfluxDbService](element_icons/InfluxDbService.png)
| [`SQLService`](#sqlservice-in-pydagservicesdbsqlservicepy) |  | ![SQLService](element_icons/SQLService.png)
| [`CopyFileService`](#copyfileservice-in-pydagservicesdocumentscopyfileservicepy) | `Service`to copy files from one location to another | ![CopyFileService](element_icons/CopyFileService.png)
| [`DeleteFileService`](#deletefileservice-in-pydagservicesdocumentsdeletefileservicepy) | `Service` to delete files from folders | ![DeleteFileService](element_icons/DeleteFileService.png)
| [`DocumentTextService`](#documenttextservice-in-pydagservicesdocumentsdocumenttextservicepy) | `MappingService` that retrieves text content from specified files         | ![DocumentTextService](element_icons/DocumentTextService.png)
| [`DocxService`](#docxservice-in-pydagservicesdocumentsdocxservicepy) | `MappingService` for writing data to DOCX documents.The specified addresses in `write_to_sink` can be used to map data keys from buffer to place holders in word template.If no addresses are specified all buffer keys are directly mapped to the context of the word template | ![DocxService](element_icons/DocxService.png)
| [`ExcelBufferService`](#excelbufferservice-in-pydagservicesdocumentsexcelbufferservicepy) | `Service` for creating `Buffer`s in `Agent` for each named table found in specified Excel file | ![ExcelBufferService](element_icons/ExcelBufferService.png)
| [`FileEmbeddingService`](#fileembeddingservice-in-pydagservicesdocumentsfileembeddingservicepy) | File Embedding Service to embed documents from file links into an embedding store. Only text-based documents are embedded.     | ![FileEmbeddingService](element_icons/FileEmbeddingService.png)
| [`FileTextSearchService`](#filetextsearchservice-in-pydagservicesdocumentsfiletextsearchservicepy) |  | ![FileTextSearchService](element_icons/FileTextSearchService.png)
| [`FileWatchdogService`](#filewatchdogservice-in-pydagservicesdocumentsfilewatchdogservicepy) |  | ![FileWatchdogService](element_icons/FileWatchdogService.png)
| [`FolderObserveMailService`](#folderobservemailservice-in-pydagservicesdocumentsfolderobservemailservicepy) | `Service` to observe a folder for new files and alert by mail on events. | ![FolderObserveMailService](element_icons/FolderObserveMailService.png)
| [`NpzService`](#npzservice-in-pydagservicesdocumentsnpzservicepy) | `MappingService` that retrieves data from a *.npz numpy file         | ![NpzService](element_icons/NpzService.png)
| [`Backup`](#backup-in-pydagservicesdocumentsrollingbackupservicepy) |  | ![Backup](element_icons/Backup.png)
| [`RollingBackupService`](#rollingbackupservice-in-pydagservicesdocumentsrollingbackupservicepy) |  | ![RollingBackupService](element_icons/RollingBackupService.png)
| [`HttpService`](#httpservice-in-pydagserviceshttphttpservicepy) | `MappingService` for reading and writing data from/to http endpoints     | ![HttpService](element_icons/HttpService.png)
| [`LLMSQLService`](#llmsqlservice-in-pydagservicesllmllmsqlservicepy) | Service to interact with SQL databases.Taken in parts from https://python.langchain.com/docs/tutorials/sql_qa/ | ![LLMSQLService](element_icons/LLMSQLService.png)
| [`LLMService`](#llmservice-in-pydagservicesllmllmservicepy) | `Service` for chat based LLM interaction.Internet context uses Tavily and requires a Tavily API key configured as`tavily_api_key` or the `TAVILY_API_KEY` environment variable.File inputs use `context_files` and may be URLs, file URLs, local paths(absolute or relative to the current working directory), data URIs, base64strings, bytes, or lists. OPENAI and AZURE send them to the model; OLLAMAwarns and continues text-only. | ![LLMService](element_icons/LLMService.png)
| [`LLMToolService`](#llmtoolservice-in-pydagservicesllmllmtoolservicepy) |  | ![LLMToolService](element_icons/LLMToolService.png)
| [`RAGService`](#ragservice-in-pydagservicesllmragservicepy) | Retrieval Augmented Generation (RAG) Service for document based LLM knowledge retrieval in chat form.Optional per-call file context is accepted through `chat(..., context_files=...)`.External URLs, local file URLs, local paths absolute or relative to thecurrent working directory, data URIs, plain base64 strings, raw bytes, orlists of those values are accepted. File inputs are supported only forOPENAI and AZURE. OLLAMA file handling is not implemented yet; supplyingfiles with OLLAMA emits a warning and continues text-only. | ![RAGService](element_icons/RAGService.png)
| [`MQTTService`](#mqttservice-in-pydagservicesmqttmqttservicepy) | `MappingService` for subscribing or writing data from/to MQTT topics.     | ![MQTTService](element_icons/MQTTService.png)
| [`MSGraphService`](#msgraphservice-in-pydagservicesofficemsgraphservicepy) | `Service` that provieds functionalities to access Microsoft Graph API     | ![MSGraphService](element_icons/MSGraphService.png)
| [`OpcUaService`](#opcuaservice-in-pydagservicesopcuaopcuaservicepy) | `MappingService` for reading and writing data from/to OPC UA servers.     | ![OpcUaService](element_icons/OpcUaService.png)
| [`DashPlotService`](#dashplotservice-in-pydagservicesplotdashplotservicepy) |  | ![DashPlotService](element_icons/DashPlotService.png)
| [`PlotlifyService`](#plotlifyservice-in-pydagservicesplotplotlifyservicepy) |  | ![PlotlifyService](element_icons/PlotlifyService.png)
| [`S7Service`](#s7service-in-pydagservicess7s7servicepy) | `MappingService`reading from and writing to S7 PLCs.     | ![S7Service](element_icons/S7Service.png)
| [`SAPNetWeaverRFCService`](#sapnetweaverrfcservice-in-pydagservicessapsapnetweaverrfcservicepy) |  | ![SAPNetWeaverRFCService](element_icons/SAPNetWeaverRFCService.png)
| [`SAPODataService`](#sapodataservice-in-pydagservicessapsapodataservicepy) |  | ![SAPODataService](element_icons/SAPODataService.png)
| [`ByteStreamService`](#bytestreamservice-in-pydagservicessocketbytestreamservicepy) | `MappingService` to read and write byte streams from/to a socket connection.<br>The service can be configured with different byte schemas for connecting, disconnecting,sending, and receiving data.<br>The bytescheams are defined as a string of data types, e.g. "Bhf5s" -> uint8, int16, float32, string of length 5<br>The addresses in read_from_source and write_to_sink are used to specify the buffer keys to read from or write to.<br>e.g. addresses = ["B1", "B3", "SENSOR1"]<br>The length of the addresses list must not match the number of buffers passed, all buffers are being searched for the keys in addresses.But it has to match the number of elements in the schema used for reading or writing. Omiting schema fields can be done by specifying None in the addresses list.<br>For Example:<br>schema = "BfI" -> addresses = ["ID1", None, "ID3"] | ![ByteStreamService](element_icons/ByteStreamService.png)
| [`SerialService`](#serialservice-in-pydagservicessocketserialservicepy) | `ByteStreamService` for serial communication using pySerial.     | ![SerialService](element_icons/SerialService.png)
| [`TCPClientService`](#tcpclientservice-in-pydagservicessockettcpclientservicepy) |  | ![TCPClientService](element_icons/TCPClientService.png)
| [`WebSocketService`](#websocketservice-in-pydagservicessocketwebsocketservicepy) | `MappingService` for subscribing and writing data from/to WebSocket endpoints.     | ![WebSocketService](element_icons/WebSocketService.png)
| [`VSEService`](#vseservice-in-pydagservicessocketifmvsevseservicepy) |  | ![VSEService](element_icons/VSEService.png)
| [`SFCService`](#sfcservice-in-pydagservicesstatemachinesfcservicepy) |  | ![SFCService](element_icons/SFCService.png)
| [`SimpleStatemachine`](#simplestatemachine-in-pydagservicesstatemachinesimplestatemachinepy) |  | ![SimpleStatemachine](element_icons/SimpleStatemachine.png)
| [`StatemachineService`](#statemachineservice-in-pydagservicesstatemachinestatemachineservicepy) | abstract `ObserverService` class for Statemachines     | ![StatemachineService](element_icons/StatemachineService.png)
| [`TaskRunnerService`](#taskrunnerservice-in-pydagservicestaskstaskrunnerservicepy) | A Service for running conventional callables and Action/BufferNode steps in one sequence. | ![TaskRunnerService](element_icons/TaskRunnerService.png)
| [`AgentPersistService`](#agentpersistservice-in-pydagservicesutilsagentpersistservicepy) | `ObserverService` for continuously persisting `AgentElement` configurations to filesystem     | ![AgentPersistService](element_icons/AgentPersistService.png)
| [`MappingRestartService`](#mappingrestartservice-in-pydagservicesutilsmappingrestartservicepy) | An `ObserverService` that attempts restarts on failed `MappingService`'sArgs:    ObserverService (Service): parent class | ![MappingRestartService](element_icons/MappingRestartService.png)
| [`WebcamService`](#webcamservice-in-pydagservicesvisionwebcamservicepy) | An `MappingService` that captures webcam video feed into a `Buffer`     | ![WebcamService](element_icons/WebcamService.png)
| [`WebcamVideoRollbackService`](#webcamvideorollbackservice-in-pydagservicesvisionwebcamvideorollbackservicepy) | A `Service` that captures webcam video feed into video files on filesystem for x secondsand continuously creates new files,additionally only the y last files are being kept before being deleted | ![WebcamVideoRollbackService](element_icons/WebcamVideoRollbackService.png)
| [`BrowserAutomationService`](#browserautomationservice-in-pydagserviceswebbrowserbrowserautomationservicepy) |  | ![BrowserAutomationService](element_icons/BrowserAutomationService.png)
| [`HttpFileService`](#httpfileservice-in-pydagserviceswebserverhttpfileservicepy) | A `Service` that provides a webserver hosting documents from `folder_path` under localhost:{`port`}Args:    Service (_type_): _description_ | ![HttpFileService](element_icons/HttpFileService.png)
| [`HttpHTMLService`](#httphtmlservice-in-pydagserviceswebserverhttphtmlservicepy) | `Service` that provides a HTML Server that hosts the specified html content             | ![HttpHTMLService](element_icons/HttpHTMLService.png)
| [`WebService`](#webservice-in-pydagserviceswebserverwebservicepy) |  | ![WebService](element_icons/WebService.png)



## `BrowsingService` (in `pydag\services\BrowsingService.py`)

`ObserverService` Interface for discovering available data sources and their addresses.
<br>new `Services` that allow for discovery of sources and addresses must inherit this class.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `BrowsingService`
from pydag.services.BrowsingService import BrowsingService  # Adjust import if needed

browsing_service = BrowsingService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `DiscoveryService` (in `pydag\services\DiscoveryService.py`)

`Service` Interface for discovering available data sources and their addresses.
   <br>new `Service` that allow for discovery of sources and addresses must inherit this class next to `Service`.

Args:
    ObserverService (_type_): parent class for all Service, provides basic connection management and state handling
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `DiscoveryService`
from pydag.services.DiscoveryService import DiscoveryService  # Adjust import if needed

discovery_service = DiscoveryService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `MappingService` (in `pydag\services\MappingService.py`)

A `ObserverService` for mapping `Buffer`s together for reading, writing, subscribing or publishing from sources and sinks

Raises:
    ServiceException: _description_

Returns:
    _type_: _description_
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |


```python
# Example usage of `MappingService`
from pydag.services.MappingService import MappingService  # Adjust import if needed

mapping_service = MappingService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	id="<string>",
	load_on_install=False,
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True
)
```

[Go to Summary](#summary)
## `ObserverService` (in `pydag\services\ObserverService.py`)

abstract base class for Services with ObserverThreads
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |


```python
# Example usage of `ObserverService`
from pydag.services.ObserverService import ObserverService  # Adjust import if needed

observer_service = ObserverService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>"
)
```

[Go to Summary](#summary)
## `PublishService` (in `pydag\services\PublishService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `PublishService`
from pydag.services.PublishService import PublishService  # Adjust import if needed

publish_service = PublishService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `ReadService` (in `pydag\services\ReadService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `ReadService`
from pydag.services.ReadService import ReadService  # Adjust import if needed

read_service = ReadService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `Service` (in `pydag\services\Service.py`)

abstract base class for agent Services
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |


```python
# Example usage of `Service`
from pydag.services.Service import Service  # Adjust import if needed

service = Service(
	id="<string>",
	load_on_install=False,
	auto_start=True
)
```

[Go to Summary](#summary)
## `SubscribeService` (in `pydag\services\SubscribeService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `SubscribeService`
from pydag.services.SubscribeService import SubscribeService  # Adjust import if needed

subscribe_service = SubscribeService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `WriteService` (in `pydag\services\WriteService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `WriteService`
from pydag.services.WriteService import WriteService  # Adjust import if needed

write_service = WriteService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `AdsService` (in `pydag\services\ads\AdsService.py`)

`MappingService` for reading and writing data from/to Beckhoff TwinCAT PLCs via ADS (Automation Device Specification).
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `ams_net_id` | `str` | `"<string>"` | AMS Net Id to connect to for ADS Connection |
| `ip_address` | `str` | `"<string>"` | explicitly defined IP address, if it can't be extracted from AMS Net Id |
| `twincat` | `int` | `3` | Twincat version to use, e.g. 2 or 3 for TwinCAT 2/3 |


```python
# Example usage of `AdsService`
from pydag.services.ads.AdsService import AdsService  # Adjust import if needed

ads_service = AdsService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	ams_net_id="<string>",
	ip_address="<string>",
	twincat=3
)
```

[Go to Summary](#summary)
## `AudioService` (in `pydag\services\audio\AudioService.py`)

`SubscribeService` for subscribing to a system's audio input channels (e.g. from a USB microphone) using the `sounddevice` library.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `sample_rate` | `int` | `44100` | sample rate of audio channel, usually 44100 Hz |
| `device` | `int` | `1` | device number to use as input stream, if nothing is specified the default device is used |


```python
# Example usage of `AudioService`
from pydag.services.audio.AudioService import AudioService  # Adjust import if needed

audio_service = AudioService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	sample_rate=44100,
	device=1
)
```

[Go to Summary](#summary)
## `SolidPDMService` (in `pydag\services\cad\SolidPDMService.py`)

`Service` for high-level wrapping of SolidWorks PDM Professional COM API.
Wraps common vault, file, search, and workflow operations.

for help goto:
- https://help.solidworks.com/2023/english/api/epdmapi/Welcome-epdmapi.html?utm_source=chatgpt.com
- https://github.com/BlueByteSystemsInc/SOLIDWORKS-PDM-API-SDK?utm_source=chatgpt.com
- https://www.codestack.net/
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `vault_name` | `str` | `"John Doe"` |  |
| `user` | `str` | `"<string>"` |  |
| `password` | `str` | `"<string>"` |  |


```python
# Example usage of `SolidPDMService`
from pydag.services.cad.SolidPDMService import SolidPDMService  # Adjust import if needed

solid_p_d_m_service = SolidPDMService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	vault_name="John Doe",
	user="<string>",
	password="<string>"
)
```

[Go to Summary](#summary)
## `SolidWorksService` (in `pydag\services\cad\SolidWorksService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `SolidWorksService`
from pydag.services.cad.SolidWorksService import SolidWorksService  # Adjust import if needed

solid_works_service = SolidWorksService(
	auto_start=True,
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `CsvReadService` (in `pydag\services\csv\CsvReadService.py`)

`MappingService` for reading data from CSV files.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `file_path` | `str` | `"path/to/file.txt"` | path to the csv file to read |
| `mode` | `str` | `'CsvReadMode.ONE_AT_A_TIME.value'` | read mode: ALL_AT_ONCE|ONE_AT_A_TIME|LOOP |
| `delimiter` | `str` | `';'` | delimiter to use to separate columns |
| `has_header` | `bool` | `True` | specifies whether a header is present in data |
| `auto_detect` | `bool` | `False` | specifies whether to use the csv sniffing option |
| `force_numeric` | `bool` | `True` | forces numeric parsing of data |
| `encoding` | `str` | `'utf-8'` | encoding of the csv file |


```python
# Example usage of `CsvReadService`
from pydag.services.csv.CsvReadService import CsvReadService  # Adjust import if needed

csv_read_service = CsvReadService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	file_path="path/to/file.txt",
	mode='CsvReadMode.ONE_AT_A_TIME.value',
	delimiter=';',
	has_header=True,
	auto_detect=False,
	force_numeric=True,
	encoding='utf-8'
)
```

[Go to Summary](#summary)
## `CsvWriteService` (in `pydag\services\csv\CsvWriteService.py`)

`WriteService` for writing data to CSV files.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `folder` | `str` | `"path/to/folder"` | folder to save the csv files to |
| `file_post_fix` | `str` | `"path/to/file.txt"` | postfix to use with every file |
| `file_extension` | `str` | `'csv'` | extension of the files being created, specify without *.*, e.g. 'csv' or 'txt' |
| `max_samples` | `int` | `1000000` | maximum number of samples in one file, if limit is reached a new file is being created |
| `delimiter` | `str` | `';'` | delimiter to use for column separation |
| `decimal_precision` | `int` | `3` | maximum decimal precision of numeric values |
| `file_prefix_format` | `str` | `"path/to/file.txt"` | format of the timestamp prefix, if None then a unixtimestamp is used, otherwise formats like '%Y%m%d' can be specified |


```python
# Example usage of `CsvWriteService`
from pydag.services.csv.CsvWriteService import CsvWriteService  # Adjust import if needed

csv_write_service = CsvWriteService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	folder="path/to/folder",
	file_post_fix="path/to/file.txt",
	file_extension='csv',
	max_samples=1000000,
	delimiter=';',
	decimal_precision=3,
	file_prefix_format="path/to/file.txt"
)
```

[Go to Summary](#summary)
## `DataModelService` (in `pydag\services\datamodel\DataModelService.py`)

`Service` that enables modeling of data, in terms of script based computations on complex data relationships (e.g. to model machine elements or similar)
<br>Model execution / model handler
this file aggregates a chain of method calls, depending on the dependencies of the methods on dataclass variables.
This means that only those methods are executed whose variables have changed.
The model handler also registers variable inputs (from outside) and method outputs and then initiates the execution of methods accordingly.
<br>
<br>Example of a model file:
```python
import pandas as pd
from pydag.services.datamodel.DataModel import DataModel

@dataclass
class SimpleDataModel(DataModel):

    a : float = field(default=None, metadata={"description": "variable 1"})
    b : float = field(default=None, metadata={"description": "variable 2"})
    c : float = field(default=None, metadata={"description": "variable 3", "hidden": True})
    t : str = field(default=None, metadata={"description": "text variable 1", "hidden": True})

    def method1(self):
        self.b = self.a * 2 + 10.0
        self.c = self.a + self.c
    
    def method2(self):
        self.t = f"Hello World {self.c}"
    
    def method3(self, dms : DataModelService):
        df = dms.lookup_table('NAME_OF_TABLE')
        values = df.query(f"COL1 > 30 and COL2 <= {self.a}")
        self.value = values["COL1"].to_list()[0]    

```

<br>The model files always have to inherit from `DataModel`, they are `dataclasses` and all properties should be introduced as `fields`.
<br>
<br>As an additional argument to `DataModel` methods the argument `dms` of type `DataModelService` can be passed, which allows acces to the lookup-tables via dms.lookup_store([Name of the table]) with Pandas Dataframes can be provided in order to lookup values based on model variables
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `model_path` | `str` | `"<string>"` | path of the model.py file |
| `model_name` | `str` | `"John Doe"` | name of the class to load from the model.py file |


```python
# Example usage of `DataModelService`
from pydag.services.datamodel.DataModelService import DataModelService  # Adjust import if needed

data_model_service = DataModelService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	model_path="<string>",
	model_name="John Doe"
)
```

[Go to Summary](#summary)
## `MultiModelService` (in `pydag\services\datamodel\MultiModelService.py`)

`Service` that allows the management of multiple `Datamodel`s at once, enhancing the `DataModelService` capabilities
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `model_paths` | `list[str]` | `"<string>"` | paths of the model.py files |
| `model_names` | `list[str]` | `"John Doe"` | name of the classes to load from the model.py file |


```python
# Example usage of `MultiModelService`
from pydag.services.datamodel.MultiModelService import MultiModelService  # Adjust import if needed

multi_model_service = MultiModelService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	model_paths="<string>",
	model_names="John Doe"
)
```

[Go to Summary](#summary)
## `InfluxDbService` (in `pydag\services\db\InfluxDbService.py`)

`MappingService` thats reads or writes to InfluxDB.
<br>Address Schema:
<br>address = "b=[bucket];m=[measurement];f=[field]"
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `endpoint` | `str` | `'http://localhost:8086'` | The endpoint URL for the InfluxDB instance. |
| `token` | `str` | `"<string>"` | The authentication token for InfluxDB. |
| `org` | `str` | `'my-org'` | The organization name in InfluxDB. |


```python
# Example usage of `InfluxDbService`
from pydag.services.db.InfluxDbService import InfluxDbService  # Adjust import if needed

influx_db_service = InfluxDbService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	endpoint='http://localhost:8086',
	token="<string>",
	org='my-org'
)
```

[Go to Summary](#summary)
## `SQLService` (in `pydag\services\db\SQLService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `connection_str` | `str` | `"<string>"` | connection string for the specific SQL database |


```python
# Example usage of `SQLService`
from pydag.services.db.SQLService import SQLService  # Adjust import if needed

s_q_l_service = SQLService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	connection_str="<string>"
)
```

[Go to Summary](#summary)
## `CopyFileService` (in `pydag\services\documents\CopyFileService.py`)

`Service`to copy files from one location to another
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `source_folders` | `list[str]` | `'list()'` | List of source folders to copy files from. |
| `target_folder` | `str` | `"path/to/folder"` | Target folder where files will be copied to. |
| `move` | `bool` | `False` | If True, files will be moved instead of copied. |
| `older_than_milliseconds` | `int` | `1` | If set, only files older than this time will be copied or moved. |
| `thread_type` | `str` | `'ThreadType.SECOND.value'` | second precision observerthread |
| `observing_time` | `int` | `'60 * 60 * 24'` | Interval in seconds to check for new files. |


```python
# Example usage of `CopyFileService`
from pydag.services.documents.CopyFileService import CopyFileService  # Adjust import if needed

copy_file_service = CopyFileService(
	auto_start=True,
	week_days="<string>",
	id="<string>",
	load_on_install=False,
	source_folders='list()',
	target_folder="path/to/folder",
	move=False,
	older_than_milliseconds=1,
	thread_type='ThreadType.SECOND.value',
	observing_time='60 * 60 * 24'
)
```

[Go to Summary](#summary)
## `DeleteFileService` (in `pydag\services\documents\DeleteFileService.py`)

`Service` to delete files from folders
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `folders` | `list[str]` | `'list()'` | List of folders to delete files from. |
| `older_than_milliseconds` | `int` | `1` | If set, only files older than this time will be deleted. |
| `thread_type` | `str` | `'ThreadType.SECOND.value'` | second precision observerthread |
| `observing_time` | `int` | `'60 * 60 * 24'` | Interval in seconds to check for new files. |


```python
# Example usage of `DeleteFileService`
from pydag.services.documents.DeleteFileService import DeleteFileService  # Adjust import if needed

delete_file_service = DeleteFileService(
	auto_start=True,
	week_days="<string>",
	id="<string>",
	load_on_install=False,
	folders='list()',
	older_than_milliseconds=1,
	thread_type='ThreadType.SECOND.value',
	observing_time='60 * 60 * 24'
)
```

[Go to Summary](#summary)
## `DocumentTextService` (in `pydag\services\documents\DocumentTextService.py`)

`MappingService` that retrieves text content from specified files
    
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `file_path` | `str` | `"path/to/file.txt"` | the path to a file or a folder, that shall be screened for document texts |


```python
# Example usage of `DocumentTextService`
from pydag.services.documents.DocumentTextService import DocumentTextService  # Adjust import if needed

document_text_service = DocumentTextService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	file_path="path/to/file.txt"
)
```

[Go to Summary](#summary)
## `DocxService` (in `pydag\services\documents\DocxService.py`)

`MappingService` for writing data to DOCX documents.

The specified addresses in `write_to_sink` can be used to map data keys from buffer to place holders in word template.
If no addresses are specified all buffer keys are directly mapped to the context of the word template
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `output_path` | `str` | `'output.docx'` |  |
| `template_path` | `str` | `"<string>"` |  |


```python
# Example usage of `DocxService`
from pydag.services.documents.DocxService import DocxService  # Adjust import if needed

docx_service = DocxService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	output_path='output.docx',
	template_path="<string>"
)
```

[Go to Summary](#summary)
## `ExcelBufferService` (in `pydag\services\documents\ExcelBufferService.py`)

`Service` for creating `Buffer`s in `Agent` for each named table found in specified Excel file
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `excel_file` | `str` | `"path/to/file.txt"` | path of the excel file to open for tables |


```python
# Example usage of `ExcelBufferService`
from pydag.services.documents.ExcelBufferService import ExcelBufferService  # Adjust import if needed

excel_buffer_service = ExcelBufferService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	excel_file="path/to/file.txt"
)
```

[Go to Summary](#summary)
## `FileEmbeddingService` (in `pydag\services\documents\FileEmbeddingService.py`)

File Embedding Service to embed documents from file links into an embedding store. Only text-based documents are embedded.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `docs_folder` | `list[str] | str` | `"path/to/folder"` | Folder links to load documents from into embedded store on startup |
| `embedding_model_name` | `str` | `'all-MiniLM-L6-v2'` | name of the embedding model to use for embedding store. Currently, only sentence transformer models are supported, e.g. all-MiniLM-L6-v2. See  |
| `store_name` | `str` | `"John Doe"` | name of the embedded store |


```python
# Example usage of `FileEmbeddingService`
from pydag.services.documents.FileEmbeddingService import FileEmbeddingService  # Adjust import if needed

file_embedding_service = FileEmbeddingService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	docs_folder="path/to/folder",
	embedding_model_name='all-MiniLM-L6-v2',
	store_name="John Doe"
)
```

[Go to Summary](#summary)
## `FileTextSearchService` (in `pydag\services\documents\FileTextSearchService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `FileTextSearchService`
from pydag.services.documents.FileTextSearchService import FileTextSearchService  # Adjust import if needed

file_text_search_service = FileTextSearchService(
	auto_start=True,
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `FileWatchdogService` (in `pydag\services\documents\FileWatchdogService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `folders` | `list[str]` | `'list()'` | folders to watch for file events |
| `recursive` | `bool` | `True` | specifies whether to watch subdirectories as well |
| `buffer_id` | `str` | `"<string>"` | Buffer ID of the buffer to store the file events into, the id specified must exist amongst buffers |


```python
# Example usage of `FileWatchdogService`
from pydag.services.documents.FileWatchdogService import FileWatchdogService  # Adjust import if needed

file_watchdog_service = FileWatchdogService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	folders='list()',
	recursive=True,
	buffer_id="<string>"
)
```

[Go to Summary](#summary)
## `FolderObserveMailService` (in `pydag\services\documents\FolderObserveMailService.py`)

`Service` to observe a folder for new files and alert by mail on events.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `thread_type` | `str` | `'ThreadType.SECOND.value'` | second precision observerthread |
| `observing_time` | `int` | `'60 * 60 * 24'` | Interval in seconds to check for new files. |
| `folder` | `str` | `"path/to/folder"` | Path to the folder to observe. |
| `skip_weekends` | `bool` | `True` | If True, the service will not check for new files on weekends. |
| `max_entries` | `int` | `5` | Maximum number of entries to keep as history. |
| `list_files` | `bool` | `True` | If True, the service will list files in the mail body. |
| `html_report` | `bool` | `True` | If True, the mail will be sent as HTML. |
| `mail_action` | `MailAction` | `'MailAction()'` | MailAction object to send a mail with file infos. |
| `skip_extensions` | `list[str]` | `'list[str]()'` | specifies the file extensions that should be ignored in listing |


```python
# Example usage of `FolderObserveMailService`
from pydag.services.documents.FolderObserveMailService import FolderObserveMailService  # Adjust import if needed

folder_observe_mail_service = FolderObserveMailService(
	auto_start=True,
	week_days="<string>",
	id="<string>",
	load_on_install=False,
	thread_type='ThreadType.SECOND.value',
	observing_time='60 * 60 * 24',
	folder="path/to/folder",
	skip_weekends=True,
	max_entries=5,
	list_files=True,
	html_report=True,
	mail_action='MailAction()',
	skip_extensions='list[str]()'
)
```

[Go to Summary](#summary)
## `NpzService` (in `pydag\services\documents\NpzService.py`)

`MappingService` that retrieves data from a *.npz numpy file
    
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `file_path` | `str` | `"path/to/file.txt"` | the path to a file or a folder, that shall be screened for document texts |


```python
# Example usage of `NpzService`
from pydag.services.documents.NpzService import NpzService  # Adjust import if needed

npz_service = NpzService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	file_path="path/to/file.txt"
)
```

[Go to Summary](#summary)
## `Backup` (in `pydag\services\documents\RollingBackupService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `path` | `Path` | `"<value>"` |  |
| `timestamp` | `datetime` | `"2026-08-15T21:10:10Z"  # datetime as ISO string` |  |


```python
# Example usage of `Backup`
from pydag.services.documents.RollingBackupService import Backup  # Adjust import if needed

backup = Backup(
	id="<string>",
	load_on_install=False,
	path="<value>",
	timestamp="2026-08-15T21:10:10Z"  # datetime as ISO string
)
```

[Go to Summary](#summary)
## `RollingBackupService` (in `pydag\services\documents\RollingBackupService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `source` | `list[str] | str` | `'list()'` | a list or single folder path or filepath of which backups shall be made |
| `target` | `str` | `"<string>"` | target folder to store the backups |
| `max_backups` | `int` | `0` | defaults to 0, which means no maximum amount |
| `discard_mode` | `str` | `'DiscardMode.EQUIDISTANT.value'` |  |
| `backup_date_prefix` | `str` | `'%Y%m%d%H%M%S'` | timestamp formatted in the specified way, that is attached in front of filename |
| `zipped` | `bool` | `False` | specifies whether the backup files are being zipped in target |


```python
# Example usage of `RollingBackupService`
from pydag.services.documents.RollingBackupService import RollingBackupService  # Adjust import if needed

rolling_backup_service = RollingBackupService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	id="<string>",
	load_on_install=False,
	source='list()',
	target="<string>",
	max_backups=0,
	discard_mode='DiscardMode.EQUIDISTANT.value',
	backup_date_prefix='%Y%m%d%H%M%S',
	zipped=False
)
```

[Go to Summary](#summary)
## `HttpService` (in `pydag\services\http\HttpService.py`)

`MappingService` for reading and writing data from/to http endpoints
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `base_url` | `str` | `"https://example.com"` | base URL for the HTTP requests, e.g. http://localhost:8080/api |
| `headers` | `dict[str]` | `"<string>"` | headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'} |
| `json_path` | `bool` | `False` | if True, the response data is expected to be in JSON format and will be parsed accordingly to specification in address |


```python
# Example usage of `HttpService`
from pydag.services.http.HttpService import HttpService  # Adjust import if needed

http_service = HttpService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	base_url="https://example.com",
	headers="<string>",
	json_path=False
)
```

[Go to Summary](#summary)
## `LLMSQLService` (in `pydag\services\llm\LLMSQLService.py`)

Service to interact with SQL databases.
Taken in parts from https://python.langchain.com/docs/tutorials/sql_qa/
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `api_key` | `str` | `"<string>"` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | `"<string>"` | endpoint of the LLM provider |
| `model_provider` | `str` | `'ModelProvider.OPENAI.value'` | name of the model provider, e.g. OPENAI | OLLAMA | .... . Consider that for sensitive data, a local model provider like OLLAMA is recommended. |
| `model` | `str` | `'gpt-4.1-mini'` | name of the model, e.g. gpt-4o | gemma:1b | ... . If you use OLLAMA, the following recommendation applies: For normal tasks without any specific requirements, we recomment using 'deepseek-r1' as it is a versatile and powerful model. Alternatively you can use Llama 3.1 8B. For tasks which must be run on CPU and where inference is critical, use 'phi3.5' or if coding / JSON is of importance, 'qwen2.5:3b' is recommended as default.  |
| `retain_messages` | `bool` | `False` | specify True if you want to retain the chat history for context |
| `use_internet_context` | `bool` | `False` | Set to True to enrich prompts with Tavily internet search results before calling the model. Requires a Tavily API key. |
| `tavily_api_key` | `str` | `"<string>"` | Tavily API key for internet context. If omitted, TAVILY_API_KEY is read from the environment. |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `system_message` | `str` | `'SYS_SQL_EXPERT'` | Default System message to give to the LLM Agent |
| `sql_connection` | `str` | `"<string>"` | connection string for accessing a SQL database, e.g. SQLite -> sqlite:////path/to/sqlite.db |


```python
# Example usage of `LLMSQLService`
from pydag.services.llm.LLMSQLService import LLMSQLService  # Adjust import if needed

l_l_m_s_q_l_service = LLMSQLService(
	auto_start=True,
	api_key="<string>",
	endpoint="<string>",
	model_provider='ModelProvider.OPENAI.value',
	model='gpt-4.1-mini',
	retain_messages=False,
	use_internet_context=False,
	tavily_api_key="<string>",
	id="<string>",
	load_on_install=False,
	system_message='SYS_SQL_EXPERT',
	sql_connection="<string>"
)
```

[Go to Summary](#summary)
## `LLMService` (in `pydag\services\llm\LLMService.py`)

`Service` for chat based LLM interaction.

Internet context uses Tavily and requires a Tavily API key configured as
`tavily_api_key` or the `TAVILY_API_KEY` environment variable.

File inputs use `context_files` and may be URLs, file URLs, local paths
(absolute or relative to the current working directory), data URIs, base64
strings, bytes, or lists. OPENAI and AZURE send them to the model; OLLAMA
warns and continues text-only.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `api_key` | `str` | `"<string>"` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | `"<string>"` | endpoint of the LLM provider |
| `model_provider` | `str` | `'ModelProvider.OPENAI.value'` | name of the model provider, e.g. OPENAI | OLLAMA | .... . Consider that for sensitive data, a local model provider like OLLAMA is recommended. |
| `model` | `str` | `'gpt-4.1-mini'` | name of the model, e.g. gpt-4o | gemma:1b | ... . If you use OLLAMA, the following recommendation applies: For normal tasks without any specific requirements, we recomment using 'deepseek-r1' as it is a versatile and powerful model. Alternatively you can use Llama 3.1 8B. For tasks which must be run on CPU and where inference is critical, use 'phi3.5' or if coding / JSON is of importance, 'qwen2.5:3b' is recommended as default.  |
| `retain_messages` | `bool` | `False` | specify True if you want to retain the chat history for context |
| `system_message` | `str` | `'SYS_GENERAL_ASSISTANT'` | Default System message to give to the LLM Agent |
| `use_internet_context` | `bool` | `False` | Set to True to enrich prompts with Tavily internet search results before calling the model. Requires a Tavily API key. |
| `tavily_api_key` | `str` | `"<string>"` | Tavily API key for internet context. If omitted, TAVILY_API_KEY is read from the environment. |


```python
# Example usage of `LLMService`
from pydag.services.llm.LLMService import LLMService  # Adjust import if needed

l_l_m_service = LLMService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	api_key="<string>",
	endpoint="<string>",
	model_provider='ModelProvider.OPENAI.value',
	model='gpt-4.1-mini',
	retain_messages=False,
	system_message='SYS_GENERAL_ASSISTANT',
	use_internet_context=False,
	tavily_api_key="<string>"
)
```

[Go to Summary](#summary)
## `LLMToolService` (in `pydag\services\llm\LLMToolService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `api_key` | `str` | `"<string>"` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | `"<string>"` | endpoint of the LLM provider |
| `model_provider` | `str` | `'ModelProvider.OPENAI.value'` | name of the model provider, e.g. OPENAI | OLLAMA | .... . Consider that for sensitive data, a local model provider like OLLAMA is recommended. |
| `model` | `str` | `'gpt-4.1-mini'` | name of the model, e.g. gpt-4o | gemma:1b | ... . If you use OLLAMA, the following recommendation applies: For normal tasks without any specific requirements, we recomment using 'deepseek-r1' as it is a versatile and powerful model. Alternatively you can use Llama 3.1 8B. For tasks which must be run on CPU and where inference is critical, use 'phi3.5' or if coding / JSON is of importance, 'qwen2.5:3b' is recommended as default.  |
| `retain_messages` | `bool` | `False` | specify True if you want to retain the chat history for context |
| `system_message` | `str` | `'SYS_GENERAL_ASSISTANT'` | Default System message to give to the LLM Agent |
| `use_internet_context` | `bool` | `False` | Set to True to enrich prompts with Tavily internet search results before calling the model. Requires a Tavily API key. |
| `tavily_api_key` | `str` | `"<string>"` | Tavily API key for internet context. If omitted, TAVILY_API_KEY is read from the environment. |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `LLMToolService`
from pydag.services.llm.LLMToolService import LLMToolService  # Adjust import if needed

l_l_m_tool_service = LLMToolService(
	auto_start=True,
	api_key="<string>",
	endpoint="<string>",
	model_provider='ModelProvider.OPENAI.value',
	model='gpt-4.1-mini',
	retain_messages=False,
	system_message='SYS_GENERAL_ASSISTANT',
	use_internet_context=False,
	tavily_api_key="<string>",
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `RAGService` (in `pydag\services\llm\RAGService.py`)

Retrieval Augmented Generation (RAG) Service for document based LLM knowledge retrieval in chat form.

Optional per-call file context is accepted through `chat(..., context_files=...)`.
External URLs, local file URLs, local paths absolute or relative to the
current working directory, data URIs, plain base64 strings, raw bytes, or
lists of those values are accepted. File inputs are supported only for
OPENAI and AZURE. OLLAMA file handling is not implemented yet; supplying
files with OLLAMA emits a warning and continues text-only.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `api_key` | `str` | `"<string>"` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | `"<string>"` | endpoint of the LLM provider |
| `model_provider` | `str` | `'ModelProvider.OPENAI.value'` | name of the model provider, e.g. OPENAI | OLLAMA | .... . Consider that for sensitive data, a local model provider like OLLAMA is recommended. |
| `model` | `str` | `'gpt-4.1-mini'` | name of the model, e.g. gpt-4o | gemma:1b | ... . If you use OLLAMA, the following recommendation applies: For normal tasks without any specific requirements, we recomment using 'deepseek-r1' as it is a versatile and powerful model. Alternatively you can use Llama 3.1 8B. For tasks which must be run on CPU and where inference is critical, use 'phi3.5' or if coding / JSON is of importance, 'qwen2.5:3b' is recommended as default.  |
| `retain_messages` | `bool` | `False` | specify True if you want to retain the chat history for context |
| `system_message` | `str` | `'SYS_GENERAL_ASSISTANT'` | Default System message to give to the LLM Agent |
| `use_internet_context` | `bool` | `False` | Set to True to enrich prompts with Tavily internet search results before calling the model. Requires a Tavily API key. |
| `tavily_api_key` | `str` | `"<string>"` | Tavily API key for internet context. If omitted, TAVILY_API_KEY is read from the environment. |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `document_links` | `list[str]` | `'list()'` | list of document links to load into embedded store on startup |
| `ignore_invalid_documents` | `bool` | `False` | deprecated compatibility field (no-op) |
| `embedding_model_name` | `str` | `'all-MiniLM-L6-v2'` | name of the embedding model to use for embedding store |
| `vector_store_path` | `str` | `"<string>"` | path to a Chroma vector store directory or chroma.db/chroma.sqlite3 file. If omitted, an in-memory vector store is used. |


```python
# Example usage of `RAGService`
from pydag.services.llm.RAGService import RAGService  # Adjust import if needed

r_a_g_service = RAGService(
	auto_start=True,
	api_key="<string>",
	endpoint="<string>",
	model_provider='ModelProvider.OPENAI.value',
	model='gpt-4.1-mini',
	retain_messages=False,
	system_message='SYS_GENERAL_ASSISTANT',
	use_internet_context=False,
	tavily_api_key="<string>",
	id="<string>",
	load_on_install=False,
	document_links='list()',
	ignore_invalid_documents=False,
	embedding_model_name='all-MiniLM-L6-v2',
	vector_store_path="<string>"
)
```

[Go to Summary](#summary)
## `MQTTService` (in `pydag\services\mqtt\MQTTService.py`)

`MappingService` for subscribing or writing data from/to MQTT topics.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `endpoint` | `str` | `"<string>"` | endpoint of the MQTT broker, e.g. test.mosquitto.org (public test broker) |
| `port` | `int` | `1883` | port of the mqtt broker |
| `keep_alive` | `int` | `60` | keep alive interval with broker |
| `force_numeric` | `bool` | `False` | specifies if the payload from mqtt topics should be parsed as numeric value, rather than string |
| `retain` | `bool` | `False` | specifies whether messages should be retained on publishing |
| `qos` | `int` | `0` | quality of service parameter of mqtt publish |


```python
# Example usage of `MQTTService`
from pydag.services.mqtt.MQTTService import MQTTService  # Adjust import if needed

m_q_t_t_service = MQTTService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	endpoint="<string>",
	port=1883,
	keep_alive=60,
	force_numeric=False,
	retain=False,
	qos=0
)
```

[Go to Summary](#summary)
## `MSGraphService` (in `pydag\services\office\MSGraphService.py`)

`Service` that provieds functionalities to access Microsoft Graph API

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `client_id` | `str` | `"<string>"` | client id for the msgraph api |
| `tenant_id` | `str` | `"<string>"` | tenant id for the msgraph api |
| `client_secret` | `str` | `"<string>"` | client secret for the msgraph api |
| `msgraph_type` | `str` | `'MSGraphType.CLIENT.value'` | client secret for the msgraph api |
| `timeout` | `float` | `10` | timeout for api calls in seconds |


```python
# Example usage of `MSGraphService`
from pydag.services.office.MSGraphService import MSGraphService  # Adjust import if needed

m_s_graph_service = MSGraphService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	client_id="<string>",
	tenant_id="<string>",
	client_secret="<string>",
	msgraph_type='MSGraphType.CLIENT.value',
	timeout=10
)
```

[Go to Summary](#summary)
## `OpcUaService` (in `pydag\services\opcua\OpcUaService.py`)

`MappingService` for reading and writing data from/to OPC UA servers.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `endpoint` | `str` | `"<string>"` | endpoint of the opc ua server, e.g. opc.tcp://localhost:48010 |


```python
# Example usage of `OpcUaService`
from pydag.services.opcua.OpcUaService import OpcUaService  # Adjust import if needed

opc_ua_service = OpcUaService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	endpoint="<string>"
)
```

[Go to Summary](#summary)
## `DashPlotService` (in `pydag\services\plot\DashPlotService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `DashPlotService`
from pydag.services.plot.DashPlotService import DashPlotService  # Adjust import if needed

dash_plot_service = DashPlotService(
	auto_start=True,
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `PlotlifyService` (in `pydag\services\plot\PlotlifyService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `PlotlifyService`
from pydag.services.plot.PlotlifyService import PlotlifyService  # Adjust import if needed

plotlify_service = PlotlifyService(
	auto_start=True,
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `S7Service` (in `pydag\services\s7\S7Service.py`)

`MappingService`reading from and writing to S7 PLCs.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `host` | `str` | `'127.0.0.1'` | The IP address or hostname of the S7 PLC. |
| `rack` | `int` | `0` | The rack number of the S7 PLC. |
| `slot` | `int` | `1` | The slot number of the S7 PLC. |


```python
# Example usage of `S7Service`
from pydag.services.s7.S7Service import S7Service  # Adjust import if needed

s7_service = S7Service(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	host='127.0.0.1',
	rack=0,
	slot=1
)
```

[Go to Summary](#summary)
## `SAPNetWeaverRFCService` (in `pydag\services\sap\SAPNetWeaverRFCService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `SAPNetWeaverRFCService`
from pydag.services.sap.SAPNetWeaverRFCService import SAPNetWeaverRFCService  # Adjust import if needed

s_a_p_net_weaver_r_f_c_service = SAPNetWeaverRFCService(
	auto_start=True,
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `SAPODataService` (in `pydag\services\sap\SAPODataService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `SAPODataService`
from pydag.services.sap.SAPODataService import SAPODataService  # Adjust import if needed

s_a_p_o_data_service = SAPODataService(
	auto_start=True,
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `ByteStreamService` (in `pydag\services\socket\ByteStreamService.py`)

`MappingService` to read and write byte streams from/to a socket connection.
<br>The service can be configured with different byte schemas for connecting, disconnecting,
sending, and receiving data.
<br>The bytescheams are defined as a string of data types, e.g. "Bhf5s" -> uint8, int16, float32, string of length 5
<br>The addresses in read_from_source and write_to_sink are used to specify the buffer keys to read from or write to.
<br>e.g. addresses = ["B1", "B3", "SENSOR1"]
<br>The length of the addresses list must not match the number of buffers passed, all buffers are being searched for the keys in addresses.
But it has to match the number of elements in the schema used for reading or writing. Omiting schema fields can be done by specifying None in the addresses list.
<br>For Example:
<br>schema = "BfI" -> addresses = ["ID1", None, "ID3"]
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `host` | `str` | `"<string>"` | name of the host to connect to, e.g. IP address or COM-Port |
| `port` | `int` | `1` | port of the host to connect to, in case of Serial Protocol this is ignored |
| `timeout` | `int` | `1` | timeout in seconds for connecting to the host |
| `connect_bytes` | `bytes` | `"<value>"` | bytes to send after each connection |
| `disconnect_bytes` | `bytes` | `"<value>"` | bytes to send before each disconnection |
| `before_send_bytes` | `bytes` | `"<value>"` | bytes to send before each send |
| `after_send_bytes` | `bytes` | `"<value>"` | bytes to send after each send |
| `before_receive_bytes` | `bytes` | `"<value>"` | bytes to send before each receive |
| `after_receive_bytes` | `bytes` | `"<value>"` | bytes to send after each receive |
| `read_byte_schema` | `str` | `"<string>"` | schema of bytes to convert the received data to and store in buffers, e.g. s20iiff (string of length 20, int, int, float, float) |
| `write_byte_schema` | `str` | `"<string>"` | schema of bytes to convert the buffers data to and send it, e.g. ddfs10 (double, double, float, string of length 10) |


```python
# Example usage of `ByteStreamService`
from pydag.services.socket.ByteStreamService import ByteStreamService  # Adjust import if needed

byte_stream_service = ByteStreamService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	host="<string>",
	port=1,
	timeout=1,
	connect_bytes="<value>",
	disconnect_bytes="<value>",
	before_send_bytes="<value>",
	after_send_bytes="<value>",
	before_receive_bytes="<value>",
	after_receive_bytes="<value>",
	read_byte_schema="<string>",
	write_byte_schema="<string>"
)
```

[Go to Summary](#summary)
## `SerialService` (in `pydag\services\socket\SerialService.py`)

`ByteStreamService` for serial communication using pySerial.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `host` | `str` | `"<string>"` | name of the host to connect to, e.g. IP address or COM-Port |
| `port` | `int` | `1` | port of the host to connect to, in case of Serial Protocol this is ignored |
| `timeout` | `int` | `1` | timeout in seconds for connecting to the host |
| `connect_bytes` | `bytes` | `"<value>"` | bytes to send after each connection |
| `disconnect_bytes` | `bytes` | `"<value>"` | bytes to send before each disconnection |
| `before_send_bytes` | `bytes` | `"<value>"` | bytes to send before each send |
| `after_send_bytes` | `bytes` | `"<value>"` | bytes to send after each send |
| `before_receive_bytes` | `bytes` | `"<value>"` | bytes to send before each receive |
| `after_receive_bytes` | `bytes` | `"<value>"` | bytes to send after each receive |
| `read_byte_schema` | `str` | `"<string>"` | schema of bytes to convert the received data to and store in buffers, e.g. s20iiff (string of length 20, int, int, float, float) |
| `write_byte_schema` | `str` | `"<string>"` | schema of bytes to convert the buffers data to and send it, e.g. ddfs10 (double, double, float, string of length 10) |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `baud_rate` | `int` | `9600` | baud rate for serial communication |
| `new_line_mode` | `bool` | `True` | whether to use new line mode for parsing serial communication |
| `delimiter` | `str` | `';'` | delimiter to use in new line mode |


```python
# Example usage of `SerialService`
from pydag.services.socket.SerialService import SerialService  # Adjust import if needed

serial_service = SerialService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	host="<string>",
	port=1,
	timeout=1,
	connect_bytes="<value>",
	disconnect_bytes="<value>",
	before_send_bytes="<value>",
	after_send_bytes="<value>",
	before_receive_bytes="<value>",
	after_receive_bytes="<value>",
	read_byte_schema="<string>",
	write_byte_schema="<string>",
	id="<string>",
	load_on_install=False,
	baud_rate=9600,
	new_line_mode=True,
	delimiter=';'
)
```

[Go to Summary](#summary)
## `TCPClientService` (in `pydag\services\socket\TCPClientService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `host` | `str` | `"<string>"` | name of the host to connect to, e.g. IP address or COM-Port |
| `port` | `int` | `1` | port of the host to connect to, in case of Serial Protocol this is ignored |
| `timeout` | `int` | `1` | timeout in seconds for connecting to the host |
| `connect_bytes` | `bytes` | `"<value>"` | bytes to send after each connection |
| `disconnect_bytes` | `bytes` | `"<value>"` | bytes to send before each disconnection |
| `before_send_bytes` | `bytes` | `"<value>"` | bytes to send before each send |
| `after_send_bytes` | `bytes` | `"<value>"` | bytes to send after each send |
| `before_receive_bytes` | `bytes` | `"<value>"` | bytes to send before each receive |
| `after_receive_bytes` | `bytes` | `"<value>"` | bytes to send after each receive |
| `read_byte_schema` | `str` | `"<string>"` | schema of bytes to convert the received data to and store in buffers, e.g. s20iiff (string of length 20, int, int, float, float) |
| `write_byte_schema` | `str` | `"<string>"` | schema of bytes to convert the buffers data to and send it, e.g. ddfs10 (double, double, float, string of length 10) |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `TCPClientService`
from pydag.services.socket.TCPClientService import TCPClientService  # Adjust import if needed

t_c_p_client_service = TCPClientService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	host="<string>",
	port=1,
	timeout=1,
	connect_bytes="<value>",
	disconnect_bytes="<value>",
	before_send_bytes="<value>",
	after_send_bytes="<value>",
	before_receive_bytes="<value>",
	after_receive_bytes="<value>",
	read_byte_schema="<string>",
	write_byte_schema="<string>",
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `WebSocketService` (in `pydag\services\socket\WebSocketService.py`)

`MappingService` for subscribing and writing data from/to WebSocket endpoints.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `url` | `str` | `"https://example.com"` | socket url, e.g. wss://localhost:10001 |


```python
# Example usage of `WebSocketService`
from pydag.services.socket.WebSocketService import WebSocketService  # Adjust import if needed

web_socket_service = WebSocketService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	url="https://example.com"
)
```

[Go to Summary](#summary)
## `VSEService` (in `pydag\services\socket\ifmvse\VSEService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `host` | `str` | `'192.168.0.1'` | ip address or host name of the vse host device |
| `port` | `int` | `3321` | port of the vse host device |
| `sensor` | `int` | `1` | sensor number to measure |
| `sample_rate` | `int` | `10000` | sample rate in Hz from 1.000 Hz to 100.000 Hz |
| `timeout` | `int` | `3` | socket timeout, any blocking operation (connect, recv, send, accept) will wait max 'timeout' seconds |


```python
# Example usage of `VSEService`
from pydag.services.socket.ifmvse.VSEService import VSEService  # Adjust import if needed

v_s_e_service = VSEService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	host='192.168.0.1',
	port=3321,
	sensor=1,
	sample_rate=10000,
	timeout=3
)
```

[Go to Summary](#summary)
## `SFCService` (in `pydag\services\statemachine\SFCService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `nodes` | `dict[str, Node]` | `'dict[str, Node]()'` | dictionary of nodes in the statemachine service |
| `thread_type` | `str` | `'ThreadType.INSTANT.value'` | default thread type is INSTANT |
| `observing_time` | `int` | `0` | observing time that specifies the interval the observer thread should run for |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `retry_error_nodes` | `bool` | `False` | Statemachine object containing actions and transitions to go through to represent a state machine program flow |


```python
# Example usage of `SFCService`
from pydag.services.statemachine.SFCService import SFCService  # Adjust import if needed

s_f_c_service = SFCService(
	auto_start=True,
	week_days="<string>",
	nodes='dict[str, Node]()',
	thread_type='ThreadType.INSTANT.value',
	observing_time=0,
	id="<string>",
	load_on_install=False,
	retry_error_nodes=False
)
```

[Go to Summary](#summary)
## `SimpleStatemachine` (in `pydag\services\statemachine\SimpleStatemachine.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `nodes` | `dict[str, Node]` | `'dict[str, Node]()'` | dictionary of nodes in the statemachine service |
| `thread_type` | `str` | `'ThreadType.INSTANT.value'` | default thread type is INSTANT |
| `observing_time` | `int` | `0` | observing time that specifies the interval the observer thread should run for |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `SimpleStatemachine`
from pydag.services.statemachine.SimpleStatemachine import SimpleStatemachine  # Adjust import if needed

simple_statemachine = SimpleStatemachine(
	auto_start=True,
	week_days="<string>",
	nodes='dict[str, Node]()',
	thread_type='ThreadType.INSTANT.value',
	observing_time=0,
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `StatemachineService` (in `pydag\services\statemachine\StatemachineService.py`)

abstract `ObserverService` class for Statemachines

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `nodes` | `dict[str, Node]` | `'dict[str, Node]()'` | dictionary of nodes in the statemachine service |
| `thread_type` | `str` | `'ThreadType.INSTANT.value'` | default thread type is INSTANT |
| `observing_time` | `int` | `0` | observing time that specifies the interval the observer thread should run for |


```python
# Example usage of `StatemachineService`
from pydag.services.statemachine.StatemachineService import StatemachineService  # Adjust import if needed

statemachine_service = StatemachineService(
	auto_start=True,
	week_days="<string>",
	id="<string>",
	load_on_install=False,
	nodes='dict[str, Node]()',
	thread_type='ThreadType.INSTANT.value',
	observing_time=0
)
```

[Go to Summary](#summary)
## `TaskRunnerService` (in `pydag\services\tasks\TaskRunnerService.py`)

A Service for running conventional callables and Action/BufferNode steps in one sequence.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `task_files` | `list[str]` | `'list()'` |  |
| `task_sequence` | `list[str]` | `'list()'` |  |
| `inputs` | `list[list[str]]` | `'list()'` |  |
| `outputs` | `list[list[str]]` | `'list()'` |  |
| `auto_start` | `bool` | `False` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `'ThreadType.TRIGGERED.value'` | type of thread to use for running tasks |
| `description` | `str` | `"<string>"` | description of the task runner service |


```python
# Example usage of `TaskRunnerService`
from pydag.services.tasks.TaskRunnerService import TaskRunnerService  # Adjust import if needed

task_runner_service = TaskRunnerService(
	observing_time="<string>",
	week_days="<string>",
	id="<string>",
	load_on_install=False,
	task_files='list()',
	task_sequence='list()',
	inputs='list()',
	outputs='list()',
	auto_start=False,
	thread_type='ThreadType.TRIGGERED.value',
	description="<string>"
)
```

[Go to Summary](#summary)
## `AgentPersistService` (in `pydag\services\utils\AgentPersistService.py`)

`ObserverService` for continuously persisting `AgentElement` configurations to filesystem
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `AgentPersistService`
from pydag.services.utils.AgentPersistService import AgentPersistService  # Adjust import if needed

agent_persist_service = AgentPersistService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	id="<string>",
	load_on_install=False
)
```

[Go to Summary](#summary)
## `MappingRestartService` (in `pydag\services\utils\MappingRestartService.py`)

An `ObserverService` that attempts restarts on failed `MappingService`'s

Args:
    ObserverService (Service): parent class
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `thread_type` | `str` | `'ThreadType.SECOND'` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `10` | interval of seconds for restarts attempts |
| `max_restart_attempts` | `int` | `3` | number of consecutive restarts attempts before omitting the mapping service from restart attempts |


```python
# Example usage of `MappingRestartService`
from pydag.services.utils.MappingRestartService import MappingRestartService  # Adjust import if needed

mapping_restart_service = MappingRestartService(
	auto_start=True,
	week_days="<string>",
	id="<string>",
	load_on_install=False,
	thread_type='ThreadType.SECOND',
	observing_time=10,
	max_restart_attempts=3
)
```

[Go to Summary](#summary)
## `WebcamService` (in `pydag\services\vision\WebcamService.py`)

An `MappingService` that captures webcam video feed into a `Buffer`
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `"<string>"` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `"<string>"` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `"<string>"` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `"<string>"` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `0` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `camera_index` | `int` | `0` | indexof installed cameras |
| `resolution` | `list[int]` | `'list()'` | resolution [width, height] |
| `fps` | `int` | `30` | frames per second |
| `codec` | `str` | `'MJPG'` | video codec to use, mp4v | MJPG | H264 | XVID |
| `encode_base64` | `bool` | `False` | if set to true, the image data is converted to base64 strings |
| `data_uri_prefix` | `str` | `'data:image/jpeg;base64,'` | data URI prefix for base64 images |


```python
# Example usage of `WebcamService`
from pydag.services.vision.WebcamService import WebcamService  # Adjust import if needed

webcam_service = WebcamService(
	auto_start=True,
	thread_type="<string>",
	observing_time="<string>",
	week_days="<string>",
	buffer_ids='list()',
	addresses='list()',
	mapping_type="<string>",
	n=0,
	persistent=True,
	id="<string>",
	load_on_install=False,
	camera_index=0,
	resolution='list()',
	fps=30,
	codec='MJPG',
	encode_base64=False,
	data_uri_prefix='data:image/jpeg;base64,'
)
```

[Go to Summary](#summary)
## `WebcamVideoRollbackService` (in `pydag\services\vision\WebcamVideoRollbackService.py`)

A `Service` that captures webcam video feed into video files on filesystem for x seconds
and continuously creates new files,
additionally only the y last files are being kept before being deleted
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `output_folder` | `str` | `"path/to/folder"` | folder path to the video output folder |
| `post_fix` | `str` | `'video'` | postfix to append to each file, all the files start with timestamp |
| `extension` | `str` | `'avi'` | specifies the extension of the video file, this should match with the selected codec. mp4 -> mp4v, avi -> MJPG, ... |
| `video_length` | `float` | `60` | video length in seconds |
| `rollback_files` | `int` | `10` | number of rollback files to keep |
| `camera_index` | `int` | `0` | index of installed cameras |
| `resolution` | `list[int]` | `'list()'` | resolution [width, height] |
| `fps` | `int` | `30` | frames per second |
| `codec` | `str` | `'MJPG'` | video codec to use, mp4v | MJPG | H264 | XVID |


```python
# Example usage of `WebcamVideoRollbackService`
from pydag.services.vision.WebcamVideoRollbackService import WebcamVideoRollbackService  # Adjust import if needed

webcam_video_rollback_service = WebcamVideoRollbackService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	output_folder="path/to/folder",
	post_fix='video',
	extension='avi',
	video_length=60,
	rollback_files=10,
	camera_index=0,
	resolution='list()',
	fps=30,
	codec='MJPG'
)
```

[Go to Summary](#summary)
## `BrowserAutomationService` (in `pydag\services\webbrowser\BrowserAutomationService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `browser_type` | `str` | `'EDGE'` | type of browser, EDGE | FIREFOX | CHROME |


```python
# Example usage of `BrowserAutomationService`
from pydag.services.webbrowser.BrowserAutomationService import BrowserAutomationService  # Adjust import if needed

browser_automation_service = BrowserAutomationService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	browser_type='EDGE'
)
```

[Go to Summary](#summary)
## `HttpFileService` (in `pydag\services\webserver\HttpFileService.py`)

A `Service` that provides a webserver hosting documents from `folder_path` under localhost:{`port`}

Args:
    Service (_type_): _description_
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `folder_path` | `str` | `"path/to/folder"` |  |
| `port` | `int` | `1` |  |


```python
# Example usage of `HttpFileService`
from pydag.services.webserver.HttpFileService import HttpFileService  # Adjust import if needed

http_file_service = HttpFileService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	folder_path="path/to/folder",
	port=1
)
```

[Go to Summary](#summary)
## `HttpHTMLService` (in `pydag\services\webserver\HttpHTMLService.py`)

`Service` that provides a HTML Server that hosts the specified html content        
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `port` | `int` | `8099` | port of the http server |
| `html` | `str` | `'<h1>Hello World!</h1>'` | html to show on the website |


```python
# Example usage of `HttpHTMLService`
from pydag.services.webserver.HttpHTMLService import HttpHTMLService  # Adjust import if needed

http_h_t_m_l_service = HttpHTMLService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	port=8099,
	html='<h1>Hello World!</h1>'
)
```

[Go to Summary](#summary)
## `WebService` (in `pydag\services\webserver\WebService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `"<string>"` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `root` | `str` | `'.'` |  |
| `host` | `str` | `'0.0.0.0'` |  |
| `port` | `int` | `8080` |  |


```python
# Example usage of `WebService`
from pydag.services.webserver.WebService import WebService  # Adjust import if needed

web_service = WebService(
	auto_start=True,
	id="<string>",
	load_on_install=False,
	root='.',
	host='0.0.0.0',
	port=8080
)
```

[Go to Summary](#summary)