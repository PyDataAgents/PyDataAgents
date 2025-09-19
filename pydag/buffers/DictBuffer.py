from __future__ import annotations
import copy
import threading
import numpy as np

from ..agents.AgentConfig import AgentConfig
from .Buffer import Buffer
from ..agents import Agent

class DictBuffer(Buffer):
    """buffer that stores its values in a dictionary in a table like fashion, where every key contains a list of data
    """
        
    def __post_init__(self):
        super().__post_init__()
        self.elements : dict[list] = dict()
        self.lock = threading.RLock()

    def install(self, agent : Agent = None):
        super().install(agent)
        if self.initial_values is not None:
            self.elements = self.initial_values
        
    def deinstall(self, agent : Agent = None):
        super().deinstall(agent)
        self.elements = {}        
    
    def push(self, elements: list | dict):        
        with self.lock:
            if isinstance(elements, dict):
                for k, v in elements.items():
                    if k not in self.elements or not isinstance(self.elements[k], list):
                        self.elements[k] = []
                    if isinstance(v, list):
                        self.elements[k].extend(v)
                    else:
                        self.elements[k].append(v)

                    # enforce capacity
                    if self.capacity != AgentConfig.INFINITE_CAPACITY:
                        while len(self.elements[k]) > self.capacity:
                            self.elements[k].pop(0)

            elif isinstance(elements, list) and all(isinstance(el, dict) for el in elements):
                for el in elements:
                    self.push(el)
        

    def data(self, n=0, persistent=True) -> dict:
        if n > 0:
            if len(self.elements.keys) > 0:
                d = dict()
                for k in self.elements.keys():
                    if len(self.elements[k]) < n:
                        n = len(self.elements[k])
                    d[k] = self.elements[k][0:n]
                    if not persistent:
                        del self.elements[k][0:n]
                return d
            return None
        else:
            # always make a deep copy, otherwise a reference will be maintained
            if len(self.elements) > 0:
                d = copy.deepcopy(self.elements)
                if not persistent:
                    for k in self.elements.keys():
                        self.elements[k].clear()
                return d
            else:
                return None
            
    def data_with_meta(self, n = 0, persistent = True) -> dict:        
        d = {}
        d[AgentConfig.DATA] = self.data(n, persistent)
        d[AgentConfig.META] = self.config_options()
        return d

    def size(self) -> int:
        if len(self.elements) == 0:
            return 0
        else:
            return len(next(iter(self.elements.values())))
        
    def clear(self):
        self.elements.clear()
        
    def to_html(self) -> str:
        """
        returns this `Buffer`s data to HTML formatted Table string
        """        
        DEFAULT_CELL_STYLE : str = "border: 1px solid black; border-collapse: collapse; padding: 5px";
        
        data = self.data()
        # Transpose the data: get rows from column-based structure
        rows = zip(*data.values())
        columns = data.keys()
        # Start HTML table
        html = "<table border='1' style='" + DEFAULT_CELL_STYLE + "'>\n"

        # Add header row
        html += "  <tr>" + "".join(f"<th>{col}</th>" for col in columns) + "</tr>\n"

        # Add data rows
        for row in rows:
            html += "  <tr>" + "".join(f"<td>{val}</td>" for val in row) + "</tr>\n"

        html += "</table>"
        return html