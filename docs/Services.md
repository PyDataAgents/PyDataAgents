# Services Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`PlotService`](#plotservice-in-pydagservicesplotservicepy) |  |
| [`Service`](#service-in-pydagservicesservicepy) | abstract base class for Grabber Services     |
| [`BrowserAutomationService`](#browserautomationservice-in-pydagservicesbrowserbrowserautomationservicepy) |  |
| [`CopyFileService`](#copyfileservice-in-pydagservicesdocumentscopyfileservicepy) | `Service`to copy files from one location to another |
| [`DeleteFileService`](#deletefileservice-in-pydagservicesdocumentsdeletefileservicepy) | `Service` to delete files from folders |
| [`FileTextSearchService`](#filetextsearchservice-in-pydagservicesdocumentsfiletextsearchservicepy) |  |
| [`FileWatchdogService`](#filewatchdogservice-in-pydagservicesdocumentsfilewatchdogservicepy) |  |
| [`FolderObserveMailService`](#folderobservemailservice-in-pydagservicesdocumentsfolderobservemailservicepy) | `Service` to observe a folder for new files and alert by mail on events. |
| [`MSGraphService`](#msgraphservice-in-pydagservicesofficemsgraphservicepy) |  |
| [`ExcelRestService`](#excelrestservice-in-pydagservicesrestexcelrestservicepy) | Service for creating a REST API for accessing named Tables in Excel     |
| [`RestService`](#restservice-in-pydagservicesrestrestservicepy) | Service for creating a REST API for DataGrabber using FastAPI     |



## `PlotService` (in `pydag\services\PlotService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `PlotService`
from pydag.services.PlotService import PlotService  # Adjust import if needed

obj = PlotService()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `Service` (in `pydag\services\Service.py`)

abstract base class for Grabber Services
    
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
| `mail_action` | `MailAction` | `'None()'` | MailAction object to send a mail with file infos. |
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
obj.mail_action='None()'
obj.COL_DATE="<string>"
obj.COL_NUM_FILES="path/to/file.txt"
obj.COL_FOLDER_SIZE="path/to/folder"
obj.COL_FILE_EXTENSIONS="path/to/file.txt"
obj.COL_FILENAME="path/to/file.txt"
obj.COL_LINK="<string>"
obj.MAX_FILES=1
```

[Go to Summary](#summary)
## `MSGraphService` (in `pydag\services\office\MSGraphService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `MSGraphService`
from pydag.services.office.MSGraphService import MSGraphService  # Adjust import if needed

obj = MSGraphService()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `ExcelRestService` (in `pydag\services\rest\ExcelRestService.py`)

Service for creating a REST API for accessing named Tables in Excel
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `port` | `int` | `8001` | port of the REST API endpoint |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `excel_file` | `str` | `` | path of the excel file to open for tables |


```python
# Example usage of `ExcelRestService`
from pydag.services.rest.ExcelRestService import ExcelRestService  # Adjust import if needed

obj = ExcelRestService()
obj.port=8001
obj.id="<string>"
obj.load_on_install=False
obj.excel_file="path/to/file.txt"
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