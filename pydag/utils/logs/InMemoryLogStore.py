from __future__ import annotations
from collections import deque
from threading import Lock

from .LogStore import LogEntry, LogStore

class InMemoryLogStore(LogStore):
    def __init__(self, max_entries=1000):
        self._entries = deque(maxlen=max_entries)
        self._lock = Lock()

    def add(self, entry: LogEntry):
        with self._lock:
            self._entries.append(entry)

    def query(self, text : str = None, level : str = None, limit : int = None, thread : str = None) -> list[LogEntry]:
        with self._lock:
            result = list(self._entries)

        if level:
            x : LogEntry
            result = [
                x for x in result
                if x.level == level
            ]

        if text:
            text = text.lower()
            result = [
                x for x in result
                if text in x.message.lower()
            ]

        if thread:
            thread = thread.lower()
            result = [
                x for x in result
                if thread in x.thread.lower()
            ]
                
        if limit:
            if len(result) > limit:
                result = result[:limit]
    
        return result

    def get_thread_names(self) -> list[str]:
        x : LogEntry
        return sorted(
            {
                x.thread
                for x in self._entries
            }
        )