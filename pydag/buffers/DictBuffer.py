from __future__ import annotations
import copy
import threading
from dataclasses import dataclass, field

from ..agents.AgentConfig import AgentConfig
from .Buffer import Buffer
from ..agents import Agent

import time
import datetime

@dataclass
class DictBuffer(Buffer):
    """buffer that stores its values in a dictionary in a table like fashion, where every key contains a list of data
    """
    timestamps_enabled : bool = field(default=False, metadata={"description": "Whether timestamps are enabled for this buffer."})
    timestamps_key  : str = field(default="timestamps", metadata={"description": "The key under which timestamps are stored in the buffer."})
    timestamps_format   :str = field(default="unix", metadata={"description": "The format of the timestamps. Options are 'unix' for UNIX epoch time in seconds, 'iso' for ISO 8601 format."})
        
    def __post_init__(self):
        super().__post_init__()
        self.elements : dict[list] = dict()
        self.lock = threading.RLock()

    def install(self, agent : Agent = None):
        super().install(agent)
        if self.initial_values is not None:
            self.elements = self.initial_values
        
    def uninstall(self, agent : Agent = None):
        super().uninstall(agent)
        self.elements = {}        
    
    def push(self, elements: list | dict):        
        with self.lock:
            if isinstance(elements, dict):
                if len(self.elements) > 0:
                    # fill non-present keys in input elements with None
                    # or fill new keys from input elements inside self.elements with None
                    new_keys = elements.keys()
                    current_keys = self.elements.keys() - {self.timestamps_key} # The timestamps key should not be considered
                    if new_keys == current_keys:
                        # do nothing
                        pass
                    else:
                        # check length of elements and length of self.elements
                        if isinstance(next(iter(elements.values())), list):
                            ne = len(next(iter(elements.values()))) 
                        else:
                            ne = 1
                        if isinstance(next(iter(self.elements.values())), list):
                            ce = len(next(iter(self.elements.values())))
                        else:
                            ce = 1
                        
                        # check for new keys among input elements
                        missing_new_keys = new_keys - current_keys
                        if len(missing_new_keys) > 0:
                            for new_missing_key in missing_new_keys:
                                if ce == 1:
                                    self.elements[new_missing_key] = None
                                else:
                                    self.elements[new_missing_key] = [None] * ce
                        # check for missing keys in input elements regarding existing keys in self.elements
                        missing_current_keys = current_keys - new_keys                        
                        if len(missing_current_keys) > 0:
                            for missing_current_key in missing_current_keys:
                                if ne == 1:
                                    elements[missing_current_key] = None
                                else:
                                    elements[missing_current_key] = [None] * ne                
                self._fr = True # First Run flag
                for k, v in elements.items():
                    if k not in self.elements or not isinstance(self.elements[k], list):
                        self.elements[k] = []
                    self._add_data(k, v)
                        
                    # enforce capacity
                    if self.capacity != AgentConfig.INFINITE_CAPACITY:
                        while len(self.elements[k]) > self.capacity:
                            self.elements[k].pop(0)
                        if self.timestamps_key in self.elements:
                            while len(self.elements[self.timestamps_key]) > self.capacity:
                                self.elements[self.timestamps_key].pop(0)

            elif isinstance(elements, list) and all(isinstance(el, dict) for el in elements):
                for el in elements:
                    self.push(el)
        

    def data(self, n=0, persistent=True) -> dict:
        if n > 0:
            if len(self.elements.keys()) > 0:
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
    

       
    def _add_data(self, k, v): 
        _sv = False
        if isinstance(v, list):
            self.elements[k].extend(v)
        else:
            self.elements[k].append(v)
            _sv = True
        # Add timestamps if enabled
        if self.timestamps_enabled:
            # only add timestamps once - all key have the same length at this time
            if self._fr:
                self._fr = False
                if self.timestamps_key not in self.elements:
                    self.elements[self.timestamps_key] = []
                if _sv:
                    if self.timestamps_format == "unix":
                        timestamp = time.time()
                    elif self.timestamps_format == "iso":
                        timestamp = datetime.datetime.now().isoformat()
                    else:
                        timestamp = time.time()  # default to unix
                    self.elements[self.timestamps_key].append(timestamp)
                else:
                    if self.timestamps_format == "unix":
                        self.elements[self.timestamps_key].extend([time.time() for i in range(len(v))])
                    elif self.timestamps_format == "iso":
                        self.elements[self.timestamps_key].extend([datetime.datetime.now().isoformat() for i in range(len(v))])
                    else:
                        self.elements[self.timestamps_key].extend([time.time() for i in range(len(v))])


    
        