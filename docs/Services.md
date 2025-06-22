# + Service Documentation

## `BrowserAutomationService` (from `BrowserAutomationService.py`)

| Field | Type | Description |
|-------|------|-------------|
| `browser_type` | `str` | type of browser, EDGE | FIREFOX | CHROME |

## `LLMService` (from `LLMService.py`)

LLM Service for chat based LLM interaction

    
| Field | Type | Description |
|-------|------|-------------|
| `api_key` | `str` | api token for a web based model provider, e.g. OPENAI |
| `endpoint` | `str` | endpoint of the LLM provider |
| `model_provider` | `str` | name of the model provider, e.g. OPENAI | OLLAMA | ... |
| `model` | `str` | name of the model, e.g. gpt-4o | gemma:1b | ...  |
| `retain_messages` | `bool` | specify True if you want to retain the chat history for context |

## `PlotService` (from `PlotService.py`)

_No fields defined._

## `RAGService` (from `RAGService.py`)

Retrieval Augmented Generation (RAG) Service for document based LLM knowledge retrieval in chat form

    
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

## `ExcelRestService` (from `rest\ExcelRestService.py`)

Service for creating a REST API for accessing named Tables in Excel
    
| Field | Type | Description |
|-------|------|-------------|
| `excel_file` | `str` | path of the excel file to open for tables |

## `LLMRestService` (from `rest\LLMRestService.py`)

Service for creating a REST API for accessing LLM Models
    
_No fields defined._

## `RestService` (from `rest\RestService.py`)

Service for creating a REST API for DataGrabber using FastAPI
    
| Field | Type | Description |
|-------|------|-------------|
| `port` | `int` | port of the REST API endpoint |
