from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo
from ics import Calendar, Event

from ..NodeException import NodeException
from ...utils.FileUtils import FileUtils
from ...buffers.Buffer import Buffer
from ..Action import Action
from ..BufferNode import BufferNode

@dataclass
class ICalAction(BufferNode, Action):
    
    ical_path : str = field(default=None, metadata={"description": ""})
    date_format : str = field(default=None, metadata={"description": ""})
    name_key : str = field(default=None, metadata={"description": ""})
    start_key : str = field(default=None, metadata={"description": ""})
    end_key : str = field(default=None, metadata={"description": ""})
    duration_unit : str = field(default="hours", metadata={"description": ""})
    duration_key : str = field(default=None, metadata={"description": ""})
    description_key : str = field(default=None, metadata={"description": ""})
    location_key : str = field(default=None, metadata={"description": ""})
    time_zone : str = field(default="Europe/Berlin", metadata={"description": ""})
    
    def execute(self):
        # check for parent folder
        if not FileUtils.exists_folder(FileUtils.parent_folder(self.ical_path)):
            raise NodeException("Specified folder path in '" + self.ical_path + "' does not exist!")
        # extract data from this buffer
        data = self.buffer.data(persistent=False)
        
        if self.name_key in data and self.start_key in data and (self.end_key in data or self.duration_key in data):
            calendar = Calendar()
            e = len(data[self.name_key])
            for i in range(0, e):
                name : str = data[self.name_key][i]
                # check if start date is numeric unix timestamp
                duration = {"hours": 24}
                if isinstance(data[self.start_key][i], float) or isinstance(data[self.start_key][i], int):
                    begin : datetime = datetime.fromtimestamp(data[self.start_key][i] / 1000)                    
                    if self.end_key is not None:
                        end : datetime = datetime.fromtimestamp(data[self.end_key][i] / 1000)
                    else:
                        duration = {self.duration_unit: data[self.duration_key][i]}
                else:
                    begin_str = data[self.start_key][i]
                    if begin_str:
                        if begin_str != "":
                            begin : datetime = datetime.strptime(begin_str, self.date_format)
                            if self.end_key is not None:
                                end : datetime = datetime.strptime(data[self.end_key][i], self.date_format)
                            else:
                                duration = {self.duration_unit: data[self.duration_key][i]}
                        else:
                            continue
                    else:
                        continue                
                begin = begin.replace(tzinfo=ZoneInfo(self.time_zone))
                if end is not None:
                    end = end.replace(tzinfo=ZoneInfo(self.time_zone))                
                if self.description_key:
                    desc = data[self.description_key][i]
                else:
                    desc = None
                if self.location_key:
                    loc = data[self.location_key][i]
                else:
                    loc = None
                if self.end_key is not None:
                    # check for begin = end and make it a whole day event
                    if begin == end:
                        event = Event(name=name, begin=begin, duration={"hours": 24}, description=desc, location=loc)
                    else:
                        event = Event(name=name, begin=begin, end=end, description=desc, location=loc)
                else:
                    event = Event(name=name, begin=begin, duration=duration, description=desc, location=loc)
                calendar.events.add(event)
            with open(self.ical_path, "w", encoding = 'utf-8') as f:
                f.writelines(calendar)
        else:
            raise NodeException("one of the keys to populate ical event was not present in " + Buffer.cname())
            
        
        
        