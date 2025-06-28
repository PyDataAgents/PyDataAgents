# Services Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`BrowserAutomationService`](#browserautomationservice-from-BrowserAutomationService) |  |
| [`LLMService`](#llmservice-from-LLMService) | LLM Service for chat based LLM interaction     |
| [`PlotService`](#plotservice-from-PlotService) |  |
| [`RAGService`](#ragservice-from-RAGService) | Retrieval Augmented Generation (RAG) Service for document based LLM knowledge retrieval in chat form     |
| [`Service`](#service-from-Service) | abstract base class for Grabber Services     |
| [`FolderObserveMailService`](#folderobservemailservice-from-documents\FolderObserveMailService) | `Service` to observe a folder for new files and alert by mail on events. |
| [`ExcelRestService`](#excelrestservice-from-rest\ExcelRestService) | Service for creating a REST API for accessing named Tables in Excel     |
| [`LLMRestService`](#llmrestservice-from-rest\LLMRestService) | Service for creating a REST API for accessing LLM Models     |
| [`RestService`](#restservice-from-rest\RestService) | Service for creating a REST API for DataGrabber using FastAPI     |



## `BrowserAutomationService` (from `BrowserAutomationService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `browser_type` | `str` | `'EDGE'` | type of browser, EDGE | FIREFOX | CHROME |


```python
# Example usage of `BrowserAutomationService`
from pydatagrabber import BrowserAutomationService  # Adjust import if needed

obj = BrowserAutomationService()
obj.id="<string>"
obj.load_on_install=False
obj.browser_type='EDGE'
```

## `LLMService` (from `LLMService.py`)

LLM Service for chat based LLM interaction

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `api_key` | `str` | `` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | `` | endpoint of the LLM provider |
| `model_provider` | `str` | `` | name of the model provider, e.g. OPENAI | OLLAMA | ... |
| `model` | `str` | `` | name of the model, e.g. gpt-4o | gemma:1b | ...  |
| `retain_messages` | `bool` | `False` | specify True if you want to retain the chat history for context |


```python
# Example usage of `LLMService`
from pydatagrabber import LLMService  # Adjust import if needed

obj = LLMService()
obj.id="<string>"
obj.load_on_install=False
obj.api_key="<string>"
obj.endpoint="<string>"
obj.model_provider="<string>"
obj.model="<string>"
obj.retain_messages=False
```

## `PlotService` (from `PlotService.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `PlotService`
from pydatagrabber import PlotService  # Adjust import if needed

obj = PlotService()
obj.id="<string>"
obj.load_on_install=False
```

## `RAGService` (from `RAGService.py`)

Retrieval Augmented Generation (RAG) Service for document based LLM knowledge retrieval in chat form

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
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

obj = RAGService()
obj.id="<string>"
obj.load_on_install=False
obj.api_key="<string>"
obj.endpoint="<string>"
obj.model_provider="<string>"
obj.model="<string>"
obj.document_links='list()()'
obj.retain_messages=False
obj.ignore_invalid_documents=False
obj.embedding_model='all-MiniLM-L6-v2'
obj.persist_directory="<string>"
```

## `Service` (from `Service.py`)

abstract base class for Grabber Services
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Service`
from pydatagrabber import Service  # Adjust import if needed

obj = Service()
obj.id="<string>"
obj.load_on_install=False
```

## `FolderObserveMailService` (from `documents\FolderObserveMailService.py`)

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
from pydatagrabber import FolderObserveMailService  # Adjust import if needed

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

## `ExcelRestService` (from `rest\ExcelRestService.py`)

Service for creating a REST API for accessing named Tables in Excel
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `port` | `int` | `8001` | port of the REST API endpoint |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `excel_file` | `str` | `` | path of the excel file to open for tables |


```python
# Example usage of `ExcelRestService`
from pydatagrabber import ExcelRestService  # Adjust import if needed

obj = ExcelRestService()
obj.port=8001
obj.id="<string>"
obj.load_on_install=False
obj.excel_file="path/to/file.txt"
```

## `LLMRestService` (from `rest\LLMRestService.py`)

Service for creating a REST API for accessing LLM Models
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `port` | `int` | `8001` | port of the REST API endpoint |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `LLMRestService`
from pydatagrabber import LLMRestService  # Adjust import if needed

obj = LLMRestService()
obj.port=8001
obj.id="<string>"
obj.load_on_install=False
```

## `RestService` (from `rest\RestService.py`)

Service for creating a REST API for DataGrabber using FastAPI
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `port` | `int` | `8001` | port of the REST API endpoint |


```python
# Example usage of `RestService`
from pydatagrabber import RestService  # Adjust import if needed

obj = RestService()
obj.id="<string>"
obj.load_on_install=False
obj.port=8001
```
