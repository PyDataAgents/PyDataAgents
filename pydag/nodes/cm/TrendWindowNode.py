from dataclasses import dataclass, field
from datetime import datetime

from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode
from pydag.utils.TimeUtils import TimeUtils
from pydag.utils.SignalUtils import SignalUtils


@dataclass
class TrendWindowNode(BufferNode, Action):
    """ This `BufferNode` collects windowed data of the linked parents of specified size `n` with the current timestamp as key prefix to the original key.
    Whenever it is executed it generates a new window to keep (up to `max_windows`). If the maximum number of windows are reached, it discards the one closest to any other window, based on timestamp.

    Base Classes:
        BufferNode (_type_): _description_
        Action (_type_): _description_
    """

    max_windows : int = field(default=10, metadata={"description": "number of windows to keep"})
    date_format : str = field(default="%Y-%m-%d %H:%M:%S", metadata={"description": "dateformat to convert the new keys to"})
    date_separator : str = field(default="#", metadata={"description": "separator for splitting original key and timestamp, this should never be a word/character that could exist in the date_format"})
       
    def _on_execute(self):
        date_str = TimeUtils.datetime_to_str(datetime.now(), self.date_format).strip()
        
        # get new parent data
        parent_data = self.get_parent_data()
        if len(parent_data) > 0:
            first = next(iter(parent_data))
            if len(parent_data[first]) < self.n:
                return
            
            # old data
            old_data = self._buffer.data(n=0, persistent=False)
            self._buffer.clear()
            
            # assemble all data
            all_data = {}
            all_data.update(old_data)
            for k in parent_data.keys():
                all_data[f"{date_str}{self.date_separator}{k}"] = parent_data[k]
            
            # assemble dates and timestamps from keys
            date_groups = dict()
            timestamp_groups = dict()            
            for k, v in all_data.items():
                splits = k.split(self.date_separator)
                date_str = splits[0]
                timestamp = TimeUtils.str_to_utc(date_str, self.date_format)
                group = splits[1]
                if group not in date_groups:
                    date_groups[group] = list()
                    timestamp_groups[group] = list()
                date_groups[group].append(date_str)
                timestamp_groups[group].append(timestamp)
            
            # go through timestamps for thinning data
            new_data = {}
            new_date_group = {}
            for k, v in timestamp_groups.items():    
                _, idx = SignalUtils.timeseries_thinning(v, self.max_windows)
                new_date_group[k] = [date_groups[k][i] for i in idx]
            
            # reassemble new data with thinned timestamp keys    
            for k, date_group in new_date_group.items():
                for date_str in date_group:
                    key = f"{date_str}{self.date_separator}{k}"
                    new_data[key] = all_data[key]

            self._buffer.push(new_data)