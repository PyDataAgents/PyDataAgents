from __future__ import annotations
from nicegui import ui

from ..Agent import Agent
from .UIElements import UIPage
from ...utils.logs.LogUtils import LOGS
from ...utils.logs.LogStore import LogEntry

class UILogPage(UIPage):

    path = "/logs"
    
    def __init__(self, agent : Agent, refresh_interval : int = 1.0):
        super().__init__(agent, refresh_interval)
        self._search : str = None
        self._level : str = None
        self._thread : str = None
        self._table = None
        self._thread_select = None

    def register(self):
        
        @ui.page(self.path)
        def page():
            self._render()
            self._timer = ui.timer(self._refresh_interval, self.refresh)

    def _render(self):
        self.create_header(self.__class__.__name__)
        with ui.row():

            ui.input(placeholder="Search log messages ...").bind_value(self, "_search").on(
                "update:model-value",
                lambda _: self.refresh()
            ).classes("w-128")
            
            ui.select(
                options=[   
                    None,
                    "DEBUG",
                    "INFO",
                    "WARNING",
                    "ERROR",
                ],
                value=None,
                label="Level"
            ).bind_value(self, "_level").on(
                "update:model-value",
                lambda _: self.refresh()
            ).classes("w-32")
            
            self._thread_select = ui.select(
                options=[],
                label="Thread",
            ).classes("w-64").bind_value(self, "_thread").on(
                "update:model-value",
                lambda _: self.refresh()
            )
        
        ui.add_css("""
            .q-table thead tr th {
                font-weight: 700;
                text-align: left;
                font-size: 16px;
            }
            """)
            
        self._table = ui.table(
            columns=[
                {
                    "name": "timestamp",
                    "label": "Timestamp",
                    "field": "timestamp",
                    "align": "center"
                },
                {
                    "name": "level",
                    "label": "Level",
                    "field": "level",
                    "align": "center"
                },
                {
                    "name": "message",
                    "label": "Message",
                    "field": "message",
                    "align": "left"
                },
                {
                    "name": "thread",
                    "label": "Thread",
                    "field": "thread",
                    "align": "left"
                }
            ],
            rows=[],
            row_key="timestamp",
        ).classes("w-full")
            

    def refresh(self):
        # update thread select        
        threads = LOGS.get_thread_names()
        options = [None] + threads
        if self._thread_select.options != options:
            self._thread_select.options = options
            self._thread_select.update()
        
        # update table    
        x : LogEntry
        rows = [
            {
                "timestamp": x.timestamp,
                "level": x.level,
                "message": x.message,
                "thread": x.thread
            }
            for x in LOGS.query(
                self._search,
                self._level,
                None,
                self._thread
            )
        ]

        self._table.rows = rows
        self._table.update()