# Services Documentation

## Summary

| Class | Description | Icon |
|-------|-------------|------|
| [`ObserverService`](#observerservice-in-pydagservicesobserverservicepy) | abstract base class for Services with ObserverThreads     | ![ObserverService](element_icons/ObserverService.png)
| [`Service`](#service-in-pydagservicesservicepy) | abstract base class for agent Services     | ![Service](element_icons/Service.png)
| [`BrowserAutomationService`](#browserautomationservice-in-pydagservicesbrowserbrowserautomationservicepy) |  | ![BrowserAutomationService](element_icons/BrowserAutomationService.png)
| [`SolidPDMService`](#solidpdmservice-in-pydagservicescadsolidpdmservicepy) | `Service` for high-level wrapping of SolidWorks PDM Professional COM API.Wraps common vault, file, search, and workflow operations.for help goto:- https://help.solidworks.com/2023/english/api/epdmapi/Welcome-epdmapi.html?utm_source=chatgpt.com- https://github.com/BlueByteSystemsInc/SOLIDWORKS-PDM-API-SDK?utm_source=chatgpt.com- https://www.codestack.net/ | ![SolidPDMService](element_icons/SolidPDMService.png)
| [`SolidWorksService`](#solidworksservice-in-pydagservicescadsolidworksservicepy) |  | ![SolidWorksService](element_icons/SolidWorksService.png)
| [`DataModelService`](#datamodelservice-in-pydagservicesdatamodeldatamodelservicepy) | `Service` that enables modeling of data, in terms of script based computations on complex data relationships (e.g. to model machine elements or similar)<br>Model execution / model handlerthis file aggregates a chain of method calls, depending on the dependencies of the methods on dataclass variables.This means that only those methods are executed whose variables have changed.The model handler also registers variable inputs (from outside) and method outputs and then initiates the execution of methods accordingly.<br><br>Example of a model file:```pythonimport pandas as pdfrom pydag.services.datamodel.DataModel import DataModel@dataclassclass SimpleDataModel(DataModel):    a : float = field(default=None, metadata={"description": "variable 1"})    b : float = field(default=None, metadata={"description": "variable 2"})    c : float = field(default=None, metadata={"description": "variable 3", "hidden": True})    t : str = field(default=None, metadata={"description": "text variable 1", "hidden": True})    def method1(self):        self.b = self.a * 2 + 10.0        self.c = self.a + self.c        def method2(self):        self.t = f"Hello World {self.c}"        def method3(self, dms : DataModelService):        df = dms.lookup_table('NAME_OF_TABLE')        values = df.query(f"COL1 > 30 and COL2 <= {self.a}")        self.value = values["COL1"].to_list()[0]    ```<br>The model files always have to inherit from `DataModel`, they are `dataclasses` and all properties should be introduced as `fields`.<br><br>As an additional argument to `DataModel` methods the argument `dms` of type `DataModelService` can be passed, which allows acces to the lookup-tables via dms.lookup_store([Name of the table]) with Pandas Dataframes can be provided in order to lookup values based on model variables | ![DataModelService](element_icons/DataModelService.png)
| [`SQLService`](#sqlservice-in-pydagservicesdbsqlservicepy) |  | ![SQLService](element_icons/SQLService.png)
| [`CopyFileService`](#copyfileservice-in-pydagservicesdocumentscopyfileservicepy) | `Service`to copy files from one location to another | ![CopyFileService](element_icons/CopyFileService.png)
| [`DeleteFileService`](#deletefileservice-in-pydagservicesdocumentsdeletefileservicepy) | `Service` to delete files from folders | ![DeleteFileService](element_icons/DeleteFileService.png)
| [`ExcelBufferService`](#excelbufferservice-in-pydagservicesdocumentsexcelbufferservicepy) | `Service` for creating `Buffer`s in `Agent` for each named table found in specified Excel file | ![ExcelBufferService](element_icons/ExcelBufferService.png)
| [`FileEmbeddingService`](#fileembeddingservice-in-pydagservicesdocumentsfileembeddingservicepy) | File Embedding Service to embed documents from file links into an embedding store. Only text-based documents are embedded.     | ![FileEmbeddingService](element_icons/FileEmbeddingService.png)
| [`FileTextSearchService`](#filetextsearchservice-in-pydagservicesdocumentsfiletextsearchservicepy) |  | ![FileTextSearchService](element_icons/FileTextSearchService.png)
| [`FileWatchdogService`](#filewatchdogservice-in-pydagservicesdocumentsfilewatchdogservicepy) |  | ![FileWatchdogService](element_icons/FileWatchdogService.png)
| [`FolderObserveMailService`](#folderobservemailservice-in-pydagservicesdocumentsfolderobservemailservicepy) | `Service` to observe a folder for new files and alert by mail on events. | ![FolderObserveMailService](element_icons/FolderObserveMailService.png)
| [`HttpFileService`](#httpfileservice-in-pydagservicesdocumentshttpfileservicepy) | A `Service` that provides a webserver hosting documents from `folder_path` under localhost:{`port`}Args:    Service (_type_): _description_ | ![HttpFileService](element_icons/HttpFileService.png)
| [`HttpHTMLService`](#httphtmlservice-in-pydagservicesdocumentshttphtmlservicepy) | `Service` that provides a HTML Server that hosts the specified html content             | ![HttpHTMLService](element_icons/HttpHTMLService.png)
| [`LLMRestService`](#llmrestservice-in-pydagservicesllmllmrestservicepy) | `Service` for creating a REST API for accessing LLM Models     | ![LLMRestService](element_icons/LLMRestService.png)
| [`LLMSQLService`](#llmsqlservice-in-pydagservicesllmllmsqlservicepy) | Service to interact with SQL databases.Taken in parts from https://python.langchain.com/docs/tutorials/sql_qa/ | ![LLMSQLService](element_icons/LLMSQLService.png)
| [`LLMService`](#llmservice-in-pydagservicesllmllmservicepy) | `Service` for chat based LLM interaction     | ![LLMService](element_icons/LLMService.png)
| [`LLMToolService`](#llmtoolservice-in-pydagservicesllmllmtoolservicepy) |  | ![LLMToolService](element_icons/LLMToolService.png)
| [`RAGService`](#ragservice-in-pydagservicesllmragservicepy) | Retrieval Augmented Generation (RAG) Service for document based LLM knowledge retrieval in chat form     | ![RAGService](element_icons/RAGService.png)
| [`MappingService`](#mappingservice-in-pydagservicesmappingsmappingservicepy) | A `ObserverService` for mapping `Adapter`s and `Buffer`s together for reading, writing, subscribing or publishing from sources and sinksRaises:    ServiceException: _description_Returns:    _type_: _description_ | ![MappingService](element_icons/MappingService.png)
| [`MSGraphService`](#msgraphservice-in-pydagservicesofficemsgraphservicepy) | `Service` that provieds functionalities to access Microsoft Graph API     | ![MSGraphService](element_icons/MSGraphService.png)
| [`DashPlotService`](#dashplotservice-in-pydagservicesplotdashplotservicepy) |  | ![DashPlotService](element_icons/DashPlotService.png)
| [`PlotlifyService`](#plotlifyservice-in-pydagservicesplotplotlifyservicepy) |  | ![PlotlifyService](element_icons/PlotlifyService.png)
| [`RestService`](#restservice-in-pydagservicesrestrestservicepy) | Service for creating a REST API for DataGrabber using FastAPI     | ![RestService](element_icons/RestService.png)
| [`SFCService`](#sfcservice-in-pydagservicesstatemachinesfcservicepy) |  | ![SFCService](element_icons/SFCService.png)
| [`SimpleActionService`](#simpleactionservice-in-pydagservicesstatemachinesimpleactionservicepy) | `Service` for executing any number of `Action`s in sequence     | ![SimpleActionService](element_icons/SimpleActionService.png)
| [`SimpleStatemachine`](#simplestatemachine-in-pydagservicesstatemachinesimplestatemachinepy) |  | ![SimpleStatemachine](element_icons/SimpleStatemachine.png)
| [`StatemachineService`](#statemachineservice-in-pydagservicesstatemachinestatemachineservicepy) | abstract `ObserverService` class for Statemachines     | ![StatemachineService](element_icons/StatemachineService.png)
| [`WebcamVideoRollbackService`](#webcamvideorollbackservice-in-pydagservicesvisionwebcamvideorollbackservicepy) | A `Service` that captures webcam video feed into video files on filesystem for x secondsand continuously creates new files,additionally only the y last files are being kept before being deleted | ![WebcamVideoRollbackService](element_icons/WebcamVideoRollbackService.png)



## `ObserverService` (in `pydag\services\ObserverService.py`)

abstract base class for Services with ObserverThreads
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `thread_type` | `str` | `` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |


```python
# Example usage of `ObserverService`
from pydag.services.ObserverService import ObserverService  # Adjust import if needed

obj = ObserverService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.thread_type="<string>"
obj.observing_time="<string>"
obj.week_days="<string>"
```

[Go to Summary](#summary)
## `Service` (in `pydag\services\Service.py`)

abstract base class for agent Services
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |


```python
# Example usage of `Service`
from pydag.services.Service import Service  # Adjust import if needed

obj = Service()
obj.id="<string>"
obj.load_on_install=False
obj.auto_start=True
```

[Go to Summary](#summary)
## `BrowserAutomationService` (in `pydag\services\browser\BrowserAutomationService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `browser_type` | `str` | `'EDGE'` | type of browser, EDGE | FIREFOX | CHROME |


```python
# Example usage of `BrowserAutomationService`
from pydag.services.browser.BrowserAutomationService import BrowserAutomationService  # Adjust import if needed

obj = BrowserAutomationService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.browser_type='EDGE'
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
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `vault_name` | `str` | `` |  |
| `user` | `str` | `` |  |
| `password` | `str` | `` |  |


```python
# Example usage of `SolidPDMService`
from pydag.services.cad.SolidPDMService import SolidPDMService  # Adjust import if needed

obj = SolidPDMService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.vault_name="John Doe"
obj.user="<string>"
obj.password="<string>"
```

[Go to Summary](#summary)
## `SolidWorksService` (in `pydag\services\cad\SolidWorksService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `SolidWorksService`
from pydag.services.cad.SolidWorksService import SolidWorksService  # Adjust import if needed

obj = SolidWorksService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
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
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `model_path` | `str` | `` | path of the model.py file |
| `model_name` | `str` | `` | name of the class to load from the model.py file |


```python
# Example usage of `DataModelService`
from pydag.services.datamodel.DataModelService import DataModelService  # Adjust import if needed

obj = DataModelService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.model_path="<string>"
obj.model_name="John Doe"
```

[Go to Summary](#summary)
## `SQLService` (in `pydag\services\db\SQLService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `connection_str` | `str` | `` | connection string for the specific SQL database |


```python
# Example usage of `SQLService`
from pydag.services.db.SQLService import SQLService  # Adjust import if needed

obj = SQLService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.connection_str="<string>"
```

[Go to Summary](#summary)
## `CopyFileService` (in `pydag\services\documents\CopyFileService.py`)

`Service`to copy files from one location to another
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `source_folders` | `list[str]` | `'list()'` | List of source folders to copy files from. |
| `target_folder` | `str` | `` | Target folder where files will be copied to. |
| `move` | `bool` | `False` | If True, files will be moved instead of copied. |
| `older_than_milliseconds` | `int` | `` | If set, only files older than this time will be copied or moved. |
| `thread_type` | `str` | `'ThreadType.SECOND.value'` | second precision observerthread |
| `observing_time` | `int` | `'60 * 60 * 24'` | Interval in seconds to check for new files. |


```python
# Example usage of `CopyFileService`
from pydag.services.documents.CopyFileService import CopyFileService  # Adjust import if needed

obj = CopyFileService()
obj.auto_start=True
obj.week_days="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.source_folders='list()'
obj.target_folder="path/to/folder"
obj.move=False
obj.older_than_milliseconds=1
obj.thread_type='ThreadType.SECOND.value'
obj.observing_time='60 * 60 * 24'
```

[Go to Summary](#summary)
## `DeleteFileService` (in `pydag\services\documents\DeleteFileService.py`)

`Service` to delete files from folders
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `folders` | `list[str]` | `'list()'` | List of folders to delete files from. |
| `older_than_milliseconds` | `int` | `` | If set, only files older than this time will be deleted. |
| `thread_type` | `str` | `'ThreadType.SECOND.value'` | second precision observerthread |
| `observing_time` | `int` | `'60 * 60 * 24'` | Interval in seconds to check for new files. |


```python
# Example usage of `DeleteFileService`
from pydag.services.documents.DeleteFileService import DeleteFileService  # Adjust import if needed

obj = DeleteFileService()
obj.auto_start=True
obj.week_days="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.folders='list()'
obj.older_than_milliseconds=1
obj.thread_type='ThreadType.SECOND.value'
obj.observing_time='60 * 60 * 24'
```

[Go to Summary](#summary)
## `ExcelBufferService` (in `pydag\services\documents\ExcelBufferService.py`)

`Service` for creating `Buffer`s in `Agent` for each named table found in specified Excel file
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `excel_file` | `str` | `` | path of the excel file to open for tables |


```python
# Example usage of `ExcelBufferService`
from pydag.services.documents.ExcelBufferService import ExcelBufferService  # Adjust import if needed

obj = ExcelBufferService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.excel_file="path/to/file.txt"
```

[Go to Summary](#summary)
## `FileEmbeddingService` (in `pydag\services\documents\FileEmbeddingService.py`)

File Embedding Service to embed documents from file links into an embedding store. Only text-based documents are embedded.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `docs_folder` | `list[str] | str` | `` | Folder links to load documents from into embedded store on startup |
| `embedding_model_name` | `str` | `'all-MiniLM-L6-v2'` | name of the embedding model to use for embedding store. Currently, only sentence transformer models are supported, e.g. all-MiniLM-L6-v2. See  |
| `store_name` | `str` | `` | name of the embedded store |


```python
# Example usage of `FileEmbeddingService`
from pydag.services.documents.FileEmbeddingService import FileEmbeddingService  # Adjust import if needed

obj = FileEmbeddingService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.docs_folder="path/to/folder"
obj.embedding_model_name='all-MiniLM-L6-v2'
obj.store_name="John Doe"
```

[Go to Summary](#summary)
## `FileTextSearchService` (in `pydag\services\documents\FileTextSearchService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `FileTextSearchService`
from pydag.services.documents.FileTextSearchService import FileTextSearchService  # Adjust import if needed

obj = FileTextSearchService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `FileWatchdogService` (in `pydag\services\documents\FileWatchdogService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `folders` | `list[str]` | `'list()'` | folders to watch for file events |
| `recursive` | `bool` | `True` | specifies whether to watch subdirectories as well |
| `buffer_id` | `str` | `` | Buffer ID of the buffer to store the file events into, the id specified must exist amongst buffers |


```python
# Example usage of `FileWatchdogService`
from pydag.services.documents.FileWatchdogService import FileWatchdogService  # Adjust import if needed

obj = FileWatchdogService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.folders='list()'
obj.recursive=True
obj.buffer_id="<string>"
```

[Go to Summary](#summary)
## `FolderObserveMailService` (in `pydag\services\documents\FolderObserveMailService.py`)

`Service` to observe a folder for new files and alert by mail on events.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `thread_type` | `str` | `'ThreadType.SECOND.value'` | second precision observerthread |
| `observing_time` | `int` | `'60 * 60 * 24'` | Interval in seconds to check for new files. |
| `folder` | `str` | `` | Path to the folder to observe. |
| `skip_weekends` | `bool` | `True` | If True, the service will not check for new files on weekends. |
| `max_entries` | `int` | `5` | Maximum number of entries to keep as history. |
| `list_files` | `bool` | `True` | If True, the service will list files in the mail body. |
| `html_report` | `bool` | `True` | If True, the mail will be sent as HTML. |
| `mail_action` | `MailAction` | `'MailAction()'` | MailAction object to send a mail with file infos. |
| `skip_extensions` | `list[str]` | `'list[str]()'` | specifies the file extensions that should be ignored in listing |


```python
# Example usage of `FolderObserveMailService`
from pydag.services.documents.FolderObserveMailService import FolderObserveMailService  # Adjust import if needed

obj = FolderObserveMailService()
obj.auto_start=True
obj.week_days="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.thread_type='ThreadType.SECOND.value'
obj.observing_time='60 * 60 * 24'
obj.folder="path/to/folder"
obj.skip_weekends=True
obj.max_entries=5
obj.list_files=True
obj.html_report=True
obj.mail_action='MailAction()'
obj.skip_extensions='list[str]()'
```

[Go to Summary](#summary)
## `HttpFileService` (in `pydag\services\documents\HttpFileService.py`)

A `Service` that provides a webserver hosting documents from `folder_path` under localhost:{`port`}

Args:
    Service (_type_): _description_
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `folder_path` | `str` | `` |  |
| `port` | `int` | `` |  |


```python
# Example usage of `HttpFileService`
from pydag.services.documents.HttpFileService import HttpFileService  # Adjust import if needed

obj = HttpFileService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.folder_path="path/to/folder"
obj.port=1
```

[Go to Summary](#summary)
## `HttpHTMLService` (in `pydag\services\documents\HttpHTMLService.py`)

`Service` that provides a HTML Server that hosts the specified html content        
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `port` | `int` | `8099` | port of the http server |
| `html` | `str` | `'<h1>Hello World!</h1>'` | html to show on the website |


```python
# Example usage of `HttpHTMLService`
from pydag.services.documents.HttpHTMLService import HttpHTMLService  # Adjust import if needed

obj = HttpHTMLService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.port=8099
obj.html='<h1>Hello World!</h1>'
```

[Go to Summary](#summary)
## `LLMRestService` (in `pydag\services\llm\LLMRestService.py`)

`Service` for creating a REST API for accessing LLM Models
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `port` | `int` | `8001` | port of the REST API endpoint |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `LLMRestService`
from pydag.services.llm.LLMRestService import LLMRestService  # Adjust import if needed

obj = LLMRestService()
obj.auto_start=True
obj.port=8001
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `LLMSQLService` (in `pydag\services\llm\LLMSQLService.py`)

Service to interact with SQL databases.
Taken in parts from https://python.langchain.com/docs/tutorials/sql_qa/
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `api_key` | `str` | `` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | `` | endpoint of the LLM provider |
| `model_provider` | `str` | `'ModelProvider.OPENAI.value'` | name of the model provider, e.g. OPENAI | OLLAMA | ... |
| `model` | `str` | `'gpt-4.1-mini'` | name of the model, e.g. gpt-4o | gemma:1b | ...  |
| `retain_messages` | `bool` | `False` | specify True if you want to retain the chat history for context |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `system_message` | `str` | `'SYS_SQL_EXPERT'` | Default System message to give to the LLM Agent |
| `sql_connection` | `str` | `` | connection string for accessing a SQL database, e.g. SQLite -> sqlite:////path/to/sqlite.db |


```python
# Example usage of `LLMSQLService`
from pydag.services.llm.LLMSQLService import LLMSQLService  # Adjust import if needed

obj = LLMSQLService()
obj.auto_start=True
obj.api_key="<string>"
obj.endpoint="<string>"
obj.model_provider='ModelProvider.OPENAI.value'
obj.model='gpt-4.1-mini'
obj.retain_messages=False
obj.id="<string>"
obj.load_on_install=False
obj.system_message='SYS_SQL_EXPERT'
obj.sql_connection="<string>"
```

[Go to Summary](#summary)
## `LLMService` (in `pydag\services\llm\LLMService.py`)

`Service` for chat based LLM interaction
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `api_key` | `str` | `` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | `` | endpoint of the LLM provider |
| `model_provider` | `str` | `'ModelProvider.OPENAI.value'` | name of the model provider, e.g. OPENAI | OLLAMA | ... |
| `model` | `str` | `'gpt-4.1-mini'` | name of the model, e.g. gpt-4o | gemma:1b | ...  |
| `retain_messages` | `bool` | `False` | specify True if you want to retain the chat history for context |
| `system_message` | `str` | `'SYS_GENERAL_ASSISTANT'` | Default System message to give to the LLM Agent |


```python
# Example usage of `LLMService`
from pydag.services.llm.LLMService import LLMService  # Adjust import if needed

obj = LLMService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.api_key="<string>"
obj.endpoint="<string>"
obj.model_provider='ModelProvider.OPENAI.value'
obj.model='gpt-4.1-mini'
obj.retain_messages=False
obj.system_message='SYS_GENERAL_ASSISTANT'
```

[Go to Summary](#summary)
## `LLMToolService` (in `pydag\services\llm\LLMToolService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `api_key` | `str` | `` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | `` | endpoint of the LLM provider |
| `model_provider` | `str` | `'ModelProvider.OPENAI.value'` | name of the model provider, e.g. OPENAI | OLLAMA | ... |
| `model` | `str` | `'gpt-4.1-mini'` | name of the model, e.g. gpt-4o | gemma:1b | ...  |
| `retain_messages` | `bool` | `False` | specify True if you want to retain the chat history for context |
| `system_message` | `str` | `'SYS_GENERAL_ASSISTANT'` | Default System message to give to the LLM Agent |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `tavily_websearch_apikey` | `str` | `` |  |


```python
# Example usage of `LLMToolService`
from pydag.services.llm.LLMToolService import LLMToolService  # Adjust import if needed

obj = LLMToolService()
obj.auto_start=True
obj.api_key="<string>"
obj.endpoint="<string>"
obj.model_provider='ModelProvider.OPENAI.value'
obj.model='gpt-4.1-mini'
obj.retain_messages=False
obj.system_message='SYS_GENERAL_ASSISTANT'
obj.id="<string>"
obj.load_on_install=False
obj.tavily_websearch_apikey="<string>"
```

[Go to Summary](#summary)
## `RAGService` (in `pydag\services\llm\RAGService.py`)

Retrieval Augmented Generation (RAG) Service for document based LLM knowledge retrieval in chat form
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `api_key` | `str` | `` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | `` | endpoint of the LLM provider |
| `model_provider` | `str` | `'ModelProvider.OPENAI.value'` | name of the model provider, e.g. OPENAI | OLLAMA | ... |
| `model` | `str` | `'gpt-4.1-mini'` | name of the model, e.g. gpt-4o | gemma:1b | ...  |
| `retain_messages` | `bool` | `False` | specify True if you want to retain the chat history for context |
| `system_message` | `str` | `'SYS_GENERAL_ASSISTANT'` | Default System message to give to the LLM Agent |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `document_links` | `list[str]` | `'list()'` | list of document links to load into embedded store on startup |
| `ignore_invalid_documents` | `bool` | `False` | api token for a web based model provider, e.g. OPENAI |
| `embedding_model_name` | `str` | `'all-MiniLM-L6-v2'` | name of the embedding model to use for embedding store |
| `persist_directory` | `str` | `` | directory for persisting the embedded store |


```python
# Example usage of `RAGService`
from pydag.services.llm.RAGService import RAGService  # Adjust import if needed

obj = RAGService()
obj.auto_start=True
obj.api_key="<string>"
obj.endpoint="<string>"
obj.model_provider='ModelProvider.OPENAI.value'
obj.model='gpt-4.1-mini'
obj.retain_messages=False
obj.system_message='SYS_GENERAL_ASSISTANT'
obj.id="<string>"
obj.load_on_install=False
obj.document_links='list()'
obj.ignore_invalid_documents=False
obj.embedding_model_name='all-MiniLM-L6-v2'
obj.persist_directory="<string>"
```

[Go to Summary](#summary)
## `MappingService` (in `pydag\services\mappings\MappingService.py`)

A `ObserverService` for mapping `Adapter`s and `Buffer`s together for reading, writing, subscribing or publishing from sources and sinks

Raises:
    ServiceException: _description_

Returns:
    _type_: _description_
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `thread_type` | `str` | `` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, DAYTIME, DATE, ... |
| `observing_time` | `Union[int | str]` | `` | observing time to apply for this ObserverThread, depending on the thread type, e.g. sampling period for MILLI_SECONDS or MICRO_SECONDS, time of day for DAYTIME in %H:%M or %H:%M:%S, DATETIME dates must be specified in the format %Y-%m-%d %H:%M:%S ... |
| `week_days` | `Optional[str]` | `` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `buffer_ids` | `list[str]` | `'list()'` | list of buffer ids to map from |
| `adapter_id` | `str` | `` | id of the Adapter used for this Mapping |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `mapping_type` | `str` | `` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `1` | number of samples to insert or remove from buffers |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |


```python
# Example usage of `MappingService`
from pydag.services.mappings.MappingService import MappingService  # Adjust import if needed

obj = MappingService()
obj.auto_start=True
obj.thread_type="<string>"
obj.observing_time="<string>"
obj.week_days="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.buffer_ids='list()'
obj.adapter_id="<string>"
obj.addresses='list()'
obj.mapping_type="<string>"
obj.n=1
obj.persistent=True
```

[Go to Summary](#summary)
## `MSGraphService` (in `pydag\services\office\MSGraphService.py`)

`Service` that provieds functionalities to access Microsoft Graph API

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `client_id` | `str` | `` | client id for the msgraph api |
| `tenant_id` | `str` | `` | tenant id for the msgraph api |
| `client_secret` | `str` | `` | client secret for the msgraph api |
| `msgraph_type` | `str` | `'MSGraphType.CLIENT.value'` | client secret for the msgraph api |
| `timeout` | `float` | `10` | timeout for api calls in seconds |


```python
# Example usage of `MSGraphService`
from pydag.services.office.MSGraphService import MSGraphService  # Adjust import if needed

obj = MSGraphService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.client_id="<string>"
obj.tenant_id="<string>"
obj.client_secret="<string>"
obj.msgraph_type='MSGraphType.CLIENT.value'
obj.timeout=10
```

[Go to Summary](#summary)
## `DashPlotService` (in `pydag\services\plot\DashPlotService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `DashPlotService`
from pydag.services.plot.DashPlotService import DashPlotService  # Adjust import if needed

obj = DashPlotService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `PlotlifyService` (in `pydag\services\plot\PlotlifyService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `PlotlifyService`
from pydag.services.plot.PlotlifyService import PlotlifyService  # Adjust import if needed

obj = PlotlifyService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `RestService` (in `pydag\services\rest\RestService.py`)

Service for creating a REST API for DataGrabber using FastAPI
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `port` | `int` | `8001` | port of the REST API endpoint |


```python
# Example usage of `RestService`
from pydag.services.rest.RestService import RestService  # Adjust import if needed

obj = RestService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.port=8001
```

[Go to Summary](#summary)
## `SFCService` (in `pydag\services\statemachine\SFCService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `nodes` | `dict[str, Node]` | `'dict[str, Node]()'` | dictionary of nodes in the statemachine service |
| `thread_type` | `str` | `'ThreadType.INSTANT.value'` | default thread type is INSTANT |
| `observing_time` | `int` | `0` | observing time that specifies the interval the observer thread should run for |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `retry_error_nodes` | `bool` | `False` | Statemachine object containing actions and transitions to go through to represent a state machine program flow |


```python
# Example usage of `SFCService`
from pydag.services.statemachine.SFCService import SFCService  # Adjust import if needed

obj = SFCService()
obj.auto_start=True
obj.week_days="<string>"
obj.nodes='dict[str, Node]()'
obj.thread_type='ThreadType.INSTANT.value'
obj.observing_time=0
obj.id="<string>"
obj.load_on_install=False
obj.retry_error_nodes=False
```

[Go to Summary](#summary)
## `SimpleActionService` (in `pydag\services\statemachine\SimpleActionService.py`)

`Service` for executing any number of `Action`s in sequence
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `nodes` | `dict[str, Node]` | `'dict[str, Node]()'` | dictionary of nodes in the statemachine service |
| `thread_type` | `str` | `'ThreadType.INSTANT.value'` | default thread type is INSTANT |
| `observing_time` | `int` | `0` | observing time that specifies the interval the observer thread should run for |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `SimpleActionService`
from pydag.services.statemachine.SimpleActionService import SimpleActionService  # Adjust import if needed

obj = SimpleActionService()
obj.auto_start=True
obj.week_days="<string>"
obj.nodes='dict[str, Node]()'
obj.thread_type='ThreadType.INSTANT.value'
obj.observing_time=0
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `SimpleStatemachine` (in `pydag\services\statemachine\SimpleStatemachine.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `nodes` | `dict[str, Node]` | `'dict[str, Node]()'` | dictionary of nodes in the statemachine service |
| `thread_type` | `str` | `'ThreadType.INSTANT.value'` | default thread type is INSTANT |
| `observing_time` | `int` | `0` | observing time that specifies the interval the observer thread should run for |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `SimpleStatemachine`
from pydag.services.statemachine.SimpleStatemachine import SimpleStatemachine  # Adjust import if needed

obj = SimpleStatemachine()
obj.auto_start=True
obj.week_days="<string>"
obj.nodes='dict[str, Node]()'
obj.thread_type='ThreadType.INSTANT.value'
obj.observing_time=0
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `StatemachineService` (in `pydag\services\statemachine\StatemachineService.py`)

abstract `ObserverService` class for Statemachines

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `week_days` | `Optional[str]` | `` | specifies the week days the observer thread should run on, e.g. 'mon, fri, sun', 'mon - thu' or by numbers '0, 2, 4', where Monday = 0 and Sunday = 6 |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `nodes` | `dict[str, Node]` | `'dict[str, Node]()'` | dictionary of nodes in the statemachine service |
| `thread_type` | `str` | `'ThreadType.INSTANT.value'` | default thread type is INSTANT |
| `observing_time` | `int` | `0` | observing time that specifies the interval the observer thread should run for |


```python
# Example usage of `StatemachineService`
from pydag.services.statemachine.StatemachineService import StatemachineService  # Adjust import if needed

obj = StatemachineService()
obj.auto_start=True
obj.week_days="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.nodes='dict[str, Node]()'
obj.thread_type='ThreadType.INSTANT.value'
obj.observing_time=0
```

[Go to Summary](#summary)
## `WebcamVideoRollbackService` (in `pydag\services\vision\WebcamVideoRollbackService.py`)

A `Service` that captures webcam video feed into video files on filesystem for x seconds
and continuously creates new files,
additionally only the y last files are being kept before being deleted
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `output_folder` | `str` | `` | folder path to the video output folder |
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

obj = WebcamVideoRollbackService()
obj.auto_start=True
obj.id="<string>"
obj.load_on_install=False
obj.output_folder="path/to/folder"
obj.post_fix='video'
obj.extension='avi'
obj.video_length=60
obj.rollback_files=10
obj.camera_index=0
obj.resolution='list()'
obj.fps=30
obj.codec='MJPG'
```

[Go to Summary](#summary)