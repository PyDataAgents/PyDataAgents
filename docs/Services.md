# Services Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Service`](#service-in-pydagservicesservicepy) | abstract base class for agent Services     |
| [`BrowserAutomationService`](#browserautomationservice-in-pydagservicesbrowserbrowserautomationservicepy) |  |
| [`DataModelService`](#datamodelservice-in-pydagservicesdatamodeldatamodelservicepy) | `Service` that enables modeling of data, in terms of script based computations on complex data relationships (e.g. to model machine elements or similar)<br>Model execution / model handlerthis file aggregates a chain of method calls, depending on the dependencies of the methods on dataclass variables.This means that only those methods are executed whose variables have changed.The model handler also registers variable inputs (from outside) and method outputs and then initiates the execution of methods accordingly.<br><br>Example of a model file:```pythonimport pandas as pdfrom pydag.services.datamodel.DataModel import DataModel@dataclassclass SimpleDataModel(DataModel):    a : float = field(default=None, metadata={"description": "variable 1"})    b : float = field(default=None, metadata={"description": "variable 2"})    c : float = field(default=None, metadata={"description": "variable 3", "hidden": True})    t : str = field(default=None, metadata={"description": "text variable 1", "hidden": True})    def method1(self):        self.b = self.a * 2 + 10.0        self.c = self.a + self.c        def method2(self):        self.t = f"Hello World {self.c}"        def method3(self, dms : DataModelService):        df = dms.lookup_table('NAME_OF_TABLE')        values = df.query(f"COL1 > 30 and COL2 <= {self.a}")        self.value = values["COL1"].to_list()[0]    ```<br>The model files always have to inherit from `DataModel`, they are `dataclasses` and all properties should be introduced as `fields`.<br><br>As an additional argument to `DataModel` methods the argument `dms` of type `DataModelService` can be passed, which allows acces to the lookup-tables via dms.lookup_store([Name of the table]) with Pandas Dataframes can be provided in order to lookup values based on model variables |
| [`DataModelObserver`](#datamodelobserver-in-pydagservicesdatamodeldatamodelservicepy) |  |
| [`DataModelReadAccessVisitor`](#datamodelreadaccessvisitor-in-pydagservicesdatamodeldatamodelservicepy) |  |
| [`DataModelWriteAccessVisitor`](#datamodelwriteaccessvisitor-in-pydagservicesdatamodeldatamodelservicepy) |  |
| [`CopyFileService`](#copyfileservice-in-pydagservicesdocumentscopyfileservicepy) | `Service`to copy files from one location to another |
| [`CopyFileObserver`](#copyfileobserver-in-pydagservicesdocumentscopyfileservicepy) |  |
| [`DeleteFileService`](#deletefileservice-in-pydagservicesdocumentsdeletefileservicepy) | `Service` to delete files from folders |
| [`DeleteFileObserver`](#deletefileobserver-in-pydagservicesdocumentsdeletefileservicepy) |  |
| [`ExcelBufferService`](#excelbufferservice-in-pydagservicesdocumentsexcelbufferservicepy) | `Service` for creating `Buffer`s in `Agent` for each named table found in specified Excel file |
| [`FileTextSearchService`](#filetextsearchservice-in-pydagservicesdocumentsfiletextsearchservicepy) |  |
| [`FileWatchdogService`](#filewatchdogservice-in-pydagservicesdocumentsfilewatchdogservicepy) |  |
| [`WatchdogHandler`](#watchdoghandler-in-pydagservicesdocumentsfilewatchdogservicepy) |  |
| [`FolderObserveMailService`](#folderobservemailservice-in-pydagservicesdocumentsfolderobservemailservicepy) | `Service` to observe a folder for new files and alert by mail on events. |
| [`FolderMailObserver`](#foldermailobserver-in-pydagservicesdocumentsfolderobservemailservicepy) | Observer to handle the folder observation events. |
| [`CORSRequestHandler`](#corsrequesthandler-in-pydagservicesdocumentshttpfileservicepy) |  |
| [`HttpFileService`](#httpfileservice-in-pydagservicesdocumentshttpfileservicepy) | A `Service` that provides a webserver hosting documents from `folder_path` under localhost:{`port`}Args:    Service (_type_): _description_ |
| [`HttpHTMLService`](#httphtmlservice-in-pydagservicesdocumentshttphtmlservicepy) | `Service` that provides a HTML Server that hosts the specified html content             |
| [`MSGraphType`](#msgraphtype-in-pydagservicesofficemsgraphservicepy) |  |
| [`MSGraphService`](#msgraphservice-in-pydagservicesofficemsgraphservicepy) | `Service` that provieds functionalities to access Microsoft Graph API     |
| [`DashPlotService`](#dashplotservice-in-pydagservicesplotdashplotservicepy) |  |
| [`PlotlifyService`](#plotlifyservice-in-pydagservicesplotplotlifyservicepy) |  |
| [`RestService`](#restservice-in-pydagservicesrestrestservicepy) | Service for creating a REST API for DataGrabber using FastAPI     |
| [`SFCObserver`](#sfcobserver-in-pydagservicesstatemachinesfcservicepy) | Observer for the SFCService.This observer is be used to start the statemachine in a separate thread |
| [`SFCService`](#sfcservice-in-pydagservicesstatemachinesfcservicepy) |  |
| [`StatemachineObserver`](#statemachineobserver-in-pydagservicesstatemachinestatemachineservicepy) | Observer for the StatemachineService.This observer is be used to start the statemachine in a separate thread |
| [`StatemachineService`](#statemachineservice-in-pydagservicesstatemachinestatemachineservicepy) |  |



## `Service` (in `pydag\services\Service.py`)

abstract base class for agent Services
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Service`
from pydag.services.Service import Service  # Adjust import if needed

obj = Service()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `BrowserAutomationService` (in `pydag\services\browser\BrowserAutomationService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `browser_type` | `str` | `'EDGE'` | type of browser, EDGE | FIREFOX | CHROME |


```python
# Example usage of `BrowserAutomationService`
from pydag.services.browser.BrowserAutomationService import BrowserAutomationService  # Adjust import if needed

obj = BrowserAutomationService()
obj.id="<string>"
obj.load_on_install=False
obj.browser_type='EDGE'
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
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `model_path` | `str` | `` | path of the model.py file |
| `model_name` | `str` | `` | name of the class to load from the model.py file |


```python
# Example usage of `DataModelService`
from pydag.services.datamodel.DataModelService import DataModelService  # Adjust import if needed

obj = DataModelService()
obj.id="<string>"
obj.load_on_install=False
obj.model_path="<string>"
obj.model_name="John Doe"
```

[Go to Summary](#summary)
## `DataModelObserver` (in `pydag\services\datamodel\DataModelService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `DataModelObserver`
from pydag.services.datamodel.DataModelService import DataModelObserver  # Adjust import if needed

obj = DataModelObserver()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `DataModelReadAccessVisitor` (in `pydag\services\datamodel\DataModelService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `DataModelReadAccessVisitor`
from pydag.services.datamodel.DataModelService import DataModelReadAccessVisitor  # Adjust import if needed

obj = DataModelReadAccessVisitor()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `DataModelWriteAccessVisitor` (in `pydag\services\datamodel\DataModelService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `DataModelWriteAccessVisitor`
from pydag.services.datamodel.DataModelService import DataModelWriteAccessVisitor  # Adjust import if needed

obj = DataModelWriteAccessVisitor()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `CopyFileService` (in `pydag\services\documents\CopyFileService.py`)

`Service`to copy files from one location to another
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `source_folders` | `list[str]` | `'list()'` | List of source folders to copy files from. |
| `target_folder` | `str` | `` | Target folder where files will be copied to. |
| `move` | `bool` | `False` | If True, files will be moved instead of copied. |
| `older_than_milliseconds` | `int` | `` | If set, only files older than this time will be copied or moved. |
| `interval` | `int` | `'60 * 60 * 24'` | Interval in seconds to check for new files. |


```python
# Example usage of `CopyFileService`
from pydag.services.documents.CopyFileService import CopyFileService  # Adjust import if needed

obj = CopyFileService()
obj.id="<string>"
obj.load_on_install=False
obj.source_folders='list()'
obj.target_folder="path/to/folder"
obj.move=False
obj.older_than_milliseconds=1
obj.interval='60 * 60 * 24'
```

[Go to Summary](#summary)
## `CopyFileObserver` (in `pydag\services\documents\CopyFileService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `CopyFileObserver`
from pydag.services.documents.CopyFileService import CopyFileObserver  # Adjust import if needed

obj = CopyFileObserver()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `DeleteFileService` (in `pydag\services\documents\DeleteFileService.py`)

`Service` to delete files from folders
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `folders` | `list[str]` | `'list()'` | List of folders to delete files from. |
| `older_than_milliseconds` | `int` | `` | If set, only files older than this time will be deleted. |
| `interval` | `int` | `'60 * 60 * 24'` | Interval in seconds to check for new files. |


```python
# Example usage of `DeleteFileService`
from pydag.services.documents.DeleteFileService import DeleteFileService  # Adjust import if needed

obj = DeleteFileService()
obj.id="<string>"
obj.load_on_install=False
obj.folders='list()'
obj.older_than_milliseconds=1
obj.interval='60 * 60 * 24'
```

[Go to Summary](#summary)
## `DeleteFileObserver` (in `pydag\services\documents\DeleteFileService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `DeleteFileObserver`
from pydag.services.documents.DeleteFileService import DeleteFileObserver  # Adjust import if needed

obj = DeleteFileObserver()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `ExcelBufferService` (in `pydag\services\documents\ExcelBufferService.py`)

`Service` for creating `Buffer`s in `Agent` for each named table found in specified Excel file
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `excel_file` | `str` | `` | path of the excel file to open for tables |


```python
# Example usage of `ExcelBufferService`
from pydag.services.documents.ExcelBufferService import ExcelBufferService  # Adjust import if needed

obj = ExcelBufferService()
obj.id="<string>"
obj.load_on_install=False
obj.excel_file="path/to/file.txt"
```

[Go to Summary](#summary)
## `FileTextSearchService` (in `pydag\services\documents\FileTextSearchService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `FileTextSearchService`
from pydag.services.documents.FileTextSearchService import FileTextSearchService  # Adjust import if needed

obj = FileTextSearchService()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `FileWatchdogService` (in `pydag\services\documents\FileWatchdogService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `folders` | `list[str]` | `'list()'` | folders to watch for file events |
| `recursive` | `bool` | `True` | specifies whether to watch subdirectories as well |
| `buffer_id` | `str` | `` | Buffer ID of the buffer to store the file events into, the id specified must exist amongst buffers |


```python
# Example usage of `FileWatchdogService`
from pydag.services.documents.FileWatchdogService import FileWatchdogService  # Adjust import if needed

obj = FileWatchdogService()
obj.id="<string>"
obj.load_on_install=False
obj.folders='list()'
obj.recursive=True
obj.buffer_id="<string>"
```

[Go to Summary](#summary)
## `WatchdogHandler` (in `pydag\services\documents\FileWatchdogService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `WatchdogHandler`
from pydag.services.documents.FileWatchdogService import WatchdogHandler  # Adjust import if needed

obj = WatchdogHandler()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `FolderObserveMailService` (in `pydag\services\documents\FolderObserveMailService.py`)

`Service` to observe a folder for new files and alert by mail on events.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `folder` | `str` | `` | Path to the folder to observe. |
| `interval` | `int` | `'60 * 60 * 24'` | Interval in seconds to check the folder for new files. |
| `skip_weekends` | `bool` | `True` | If True, the service will not check for new files on weekends. |
| `max_entries` | `int` | `5` | Maximum number of entries to keep as history. |
| `list_files` | `bool` | `True` | If True, the service will list files in the mail body. |
| `html_report` | `bool` | `True` | If True, the mail will be sent as HTML. |
| `mail_action` | `MailAction` | `'MailAction()'` | MailAction object to send a mail with file infos. |
| `skip_extensions` | `list[str]` | `'list[str]()'` | specifies the file extensions that should be ignored in listing |
| `COL_DATE` | `str` | `` |  |
| `COL_NUM_FILES` | `str` | `` |  |
| `COL_FOLDER_SIZE` | `str` | `` |  |
| `COL_FILE_EXTENSIONS` | `str` | `` |  |
| `COL_FILENAME` | `str` | `` |  |
| `COL_LINK` | `str` | `` |  |
| `MAX_FILES` | `int` | `` |  |


```python
# Example usage of `FolderObserveMailService`
from pydag.services.documents.FolderObserveMailService import FolderObserveMailService  # Adjust import if needed

obj = FolderObserveMailService()
obj.id="<string>"
obj.load_on_install=False
obj.folder="path/to/folder"
obj.interval='60 * 60 * 24'
obj.skip_weekends=True
obj.max_entries=5
obj.list_files=True
obj.html_report=True
obj.mail_action='MailAction()'
obj.skip_extensions='list[str]()'
obj.COL_DATE="<string>"
obj.COL_NUM_FILES="path/to/file.txt"
obj.COL_FOLDER_SIZE="path/to/folder"
obj.COL_FILE_EXTENSIONS="path/to/file.txt"
obj.COL_FILENAME="path/to/file.txt"
obj.COL_LINK="<string>"
obj.MAX_FILES=1
```

[Go to Summary](#summary)
## `FolderMailObserver` (in `pydag\services\documents\FolderObserveMailService.py`)

Observer to handle the folder observation events.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `FolderMailObserver`
from pydag.services.documents.FolderObserveMailService import FolderMailObserver  # Adjust import if needed

obj = FolderMailObserver()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `CORSRequestHandler` (in `pydag\services\documents\HttpFileService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `CORSRequestHandler`
from pydag.services.documents.HttpFileService import CORSRequestHandler  # Adjust import if needed

obj = CORSRequestHandler()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `HttpFileService` (in `pydag\services\documents\HttpFileService.py`)

A `Service` that provides a webserver hosting documents from `folder_path` under localhost:{`port`}

Args:
    Service (_type_): _description_
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `folder_path` | `str` | `` |  |
| `port` | `int` | `` |  |


```python
# Example usage of `HttpFileService`
from pydag.services.documents.HttpFileService import HttpFileService  # Adjust import if needed

obj = HttpFileService()
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
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `port` | `int` | `8099` | port of the http server |
| `html` | `str` | `'<h1>Hello World!</h1>'` | html to show on the website |


```python
# Example usage of `HttpHTMLService`
from pydag.services.documents.HttpHTMLService import HttpHTMLService  # Adjust import if needed

obj = HttpHTMLService()
obj.id="<string>"
obj.load_on_install=False
obj.port=8099
obj.html='<h1>Hello World!</h1>'
```

[Go to Summary](#summary)
## `MSGraphType` (in `pydag\services\office\MSGraphService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `MSGraphType`
from pydag.services.office.MSGraphService import MSGraphType  # Adjust import if needed

obj = MSGraphType()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `MSGraphService` (in `pydag\services\office\MSGraphService.py`)

`Service` that provieds functionalities to access Microsoft Graph API

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
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
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `DashPlotService`
from pydag.services.plot.DashPlotService import DashPlotService  # Adjust import if needed

obj = DashPlotService()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `PlotlifyService` (in `pydag\services\plot\PlotlifyService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `PlotlifyService`
from pydag.services.plot.PlotlifyService import PlotlifyService  # Adjust import if needed

obj = PlotlifyService()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `RestService` (in `pydag\services\rest\RestService.py`)

Service for creating a REST API for DataGrabber using FastAPI
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `port` | `int` | `8001` | port of the REST API endpoint |


```python
# Example usage of `RestService`
from pydag.services.rest.RestService import RestService  # Adjust import if needed

obj = RestService()
obj.id="<string>"
obj.load_on_install=False
obj.port=8001
```

[Go to Summary](#summary)
## `SFCObserver` (in `pydag\services\statemachine\SFCService.py`)

Observer for the SFCService.
This observer is be used to start the statemachine in a separate thread
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `SFCObserver`
from pydag.services.statemachine.SFCService import SFCObserver  # Adjust import if needed

obj = SFCObserver()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `SFCService` (in `pydag\services\statemachine\SFCService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `retry_error_nodes` | `bool` | `False` | Statemachine object containing actions and transitions to go through to represent a state machine program flow |
| `start_action_id` | `str` | `` | ID of the start node in the statemachine service |
| `nodes` | `dict[str, Node]` | `'dict[str, Node]()'` | dictionary of nodes in the statemachine service |
| `thread_type` | `str` | `'ThreadType.ONLY_ONCE.value'` | the type of ObserverThread to use: ONLY_ONCE | MILLI_SECONDS | SECONDS | INSTANT | TRIGGERED |
| `sampling_period` | `int` | `0` | sampling period that specifies the interval the observer thread should run for |


```python
# Example usage of `SFCService`
from pydag.services.statemachine.SFCService import SFCService  # Adjust import if needed

obj = SFCService()
obj.id="<string>"
obj.load_on_install=False
obj.retry_error_nodes=False
obj.start_action_id="<string>"
obj.nodes='dict[str, Node]()'
obj.thread_type='ThreadType.ONLY_ONCE.value'
obj.sampling_period=0
```

[Go to Summary](#summary)
## `StatemachineObserver` (in `pydag\services\statemachine\StatemachineService.py`)

Observer for the StatemachineService.
This observer is be used to start the statemachine in a separate thread
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `StatemachineObserver`
from pydag.services.statemachine.StatemachineService import StatemachineObserver  # Adjust import if needed

obj = StatemachineObserver()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `StatemachineService` (in `pydag\services\statemachine\StatemachineService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `retry_error_nodes` | `bool` | `False` | Statemachine object containing actions and transitions to go through to represent a state machine program flow |
| `start_action_id` | `str` | `` | ID of the start node in the statemachine service |
| `nodes` | `dict[str, Node]` | `'dict[str, Node]()'` | dictionary of nodes in the statemachine service |
| `thread_type` | `str` | `'ThreadType.INSTANT.value'` |  |
| `sampling_period` | `int` | `0` | sampling period that specifies the interval the observer thread should run for |


```python
# Example usage of `StatemachineService`
from pydag.services.statemachine.StatemachineService import StatemachineService  # Adjust import if needed

obj = StatemachineService()
obj.id="<string>"
obj.load_on_install=False
obj.retry_error_nodes=False
obj.start_action_id="<string>"
obj.nodes='dict[str, Node]()'
obj.thread_type='ThreadType.INSTANT.value'
obj.sampling_period=0
```

[Go to Summary](#summary)