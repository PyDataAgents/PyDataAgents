from dataclasses import dataclass, field
from datetime import datetime
import uuid
from zoneinfo import ZoneInfo
import pytz

from ..NodeException import NodeException
from ...utils.FileUtils import FileUtils
from ...buffers.Buffer import Buffer
from ..Action import Action
from ..BufferNode import BufferNode

@dataclass
class ICalAction(BufferNode, Action):
    
    ical_path : str = field(default=None, metadata={"description": "path for ics file export, full path to the file"})
    date_format : str = field(default="%d.%m.%Y", metadata={"description": "date format to parse the incoming date fields from"})
    name_key : str = field(default=None, metadata={"description": "name of the key that contains the event name"})
    start_key : str = field(default=None, metadata={"description": "name of the key that contains the start date"})
    end_key : str = field(default=None, metadata={"description": "name of the key that contains the end date"})
    description_key : str = field(default=None, metadata={"description": "name of the key that contains the event description"})
    location_key : str = field(default=None, metadata={"description": "name of the key that contains the location of the event"})
    time_zone : str = field(default="Europe/Berlin", metadata={"description": "name of the key that contains the time zone info"})
    
    def _on_execute(self):
        # check for parent folder
        if not FileUtils.exists_folder(FileUtils.parent_folder(self.ical_path)):
            raise NodeException("Specified folder path in '" + self.ical_path + "' does not exist!")
        # extract data from this buffer
        data = self._buffer.data(persistent=False)
        
        if self.name_key in data and self.start_key in data and self.end_key in data:
            import vobject

            calendar = vobject.iCalendar()
            e = len(data[self.name_key])
            for i in range(0, e):
                name : str = data[self.name_key][i]
                # check if start date is numeric unix timestamp
                begin_str = data[self.start_key][i]
                end_str = data[self.end_key][i]
                if begin_str:
                    if begin_str != "":
                        begin : datetime = datetime.strptime(begin_str, self.date_format)
                        end : datetime = datetime.strptime(end_str, self.date_format)                        
                    else:
                        continue
                else:
                    continue                
                begin = begin.replace(tzinfo=ZoneInfo(self.time_zone))
                if end is not None:
                    end = end.replace(tzinfo=ZoneInfo(self.time_zone))
                else:
                    continue                
                if self.description_key:
                    desc = data[self.description_key][i]
                else:
                    desc = None
                if self.location_key:
                    loc = data[self.location_key][i]
                else:
                    loc = None
                vevent = calendar.add('vevent')
                vevent.add("uid").value = f"{uuid.uuid4()}"
                if loc:
                    vevent.add("location").value = loc
                if desc:
                    vevent.add("description").value = desc
                vevent.add("summary").value = name
                vevent.add("dtstamp").value = datetime.now(pytz.UTC)
                vevent.add('dtstart').value = begin
                vevent.add('dtend').value = end
                                
            with open(self.ical_path, "w", encoding = 'utf-8') as f:
                ics_str = calendar.serialize().replace('\n', '\r\n')
                f.writelines(ics_str)
        else:
            raise NodeException("one of the keys to populate ical events was not present in " + Buffer.cname())
