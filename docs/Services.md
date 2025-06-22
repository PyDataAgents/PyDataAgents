#Service Documentation

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
    api_key="example",
    endpoint="example",
    model_provider="example",
    model="example",
    retain_messages=False
)
```

## `PlotService` (from `PlotService.py`)

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
    api_key="example",
    endpoint="example",
    model_provider="example",
    model="example",
    document_links='list()()',
    retain_messages=False,
    ignore_invalid_documents=False,
    embedding_model='all-MiniLM-L6-v2',
    persist_directory="example"
)
```

## `ExcelRestService` (from `rest\ExcelRestService.py`)

Service for creating a REST API for accessing named Tables in Excel
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `excel_file` | `str` | `` | path of the excel file to open for tables |


```python
# Example usage of `ExcelRestService`
from pydatagrabber import ExcelRestService  # Adjust import if needed

obj = ExcelRestService(
    excel_file="example"
)
```

## `LLMRestService` (from `rest\LLMRestService.py`)

Service for creating a REST API for accessing LLM Models
    
_No fields defined._

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
