from __future__ import annotations
from loguru import logger


from .LogStore import LogEntry, LogStore
from .SQLiteLogStore import SQLiteLogStore
from .InMemoryLogStore import InMemoryLogStore

def logstore_sink(message):
    """ """
    record = message.record

    LOGS.add(
        LogEntry(
            timestamp=record["time"].strftime("%Y-%m-%d %H:%M:%S"),
            level=record["level"].name,
            message=record["message"],
            thread=record["thread"].name
        )
    )

def add_memory_logstore(max_entries : int = 1000):
    LOGS.set_store(InMemoryLogStore(max_entries=max_entries))
    logger.add(
        logstore_sink,
        level="DEBUG"
    )

def add_sqlite_logstore(file_name : str = "logs.db"):
    LOGS.set_store(SQLiteLogStore(file_name=file_name))
    logger.add(
        logstore_sink,
        level="DEBUG"
    )

class LogManager:
    """ """

    def __init__(self):
        self._store: LogStore | None = None

    def set_store(self, store: LogStore):
        self._store = store

    def add(self, entry: LogEntry):
        if self._store:
            self._store.add(entry)

    def query(self, text: str = None, level : str = None, limit : int = None, thread : str = None) -> list[LogEntry]:
        if not self._store:
            return []

        return self._store.query(
            text=text,
            level=level,
            limit=limit,
            thread=thread
        )
    
    def get_thread_names(self) -> list[str]:
        return self._store.get_thread_names()

LOGS : LogManager = LogManager()