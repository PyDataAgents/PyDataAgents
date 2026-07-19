from __future__ import annotations
import sqlite3

from .LogStore import LogEntry, LogStore


class SQLiteLogStore(LogStore):

    def __init__(self, file_name="logs.db"):

        self.conn = sqlite3.connect(file_name, check_same_thread=False)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                level TEXT,
                message TEXT,
                thread TEXT
            )
            """)
        self.conn.commit()

    def add(self, entry : LogEntry):
        self.conn.execute(
            """
            INSERT INTO logs
            VALUES(NULL,?,?,?,?)
            """,
            (
                entry.timestamp,
                entry.level,
                entry.message,
                entry.thread
            )
        )
        self.conn.commit()


    def query(self, text : str = None, level : str = None, limit : int = None, thread : str = None) -> list[LogEntry]:
        sql = """
        SELECT timestamp, level, message, thread
        FROM logs
        WHERE 1=1
        """

        args = []

        if level:
            sql += " AND level=?"
            args.append(level)

        if text:
            sql += " AND message LIKE ?"
            args.append(
                f"%{text}%"
            )
            
        if thread:
            sql += " AND thread LIKE ?"
            args.append(
                f"%{thread}%"
            )

        sql += """
        ORDER BY id DESC
        """

        if limit:
            sql += """
            LIMIT ?
            """
            args.append(limit)

        rows = self.conn.execute(
            sql,
            args
        )

        return [
            LogEntry(
                timestamp=r[0],
                level=r[1],
                message=r[2],
                thread=r[3]
            )
            for r in rows
        ]
        
    def get_thread_names(self) -> list[str]:
        sql = """
        SELECT UNIQUE thread
        FROM logs
        """
        rows = self.conn.execute(
            sql
        )
        return [
            r[0] for r in rows
        ]