import os
from pydag.buffers.DictBuffer import DictBuffer
from pydag.statemachine.actions.documents.ICalAction import ICalAction
from pydag.utils.FileUtils import FileUtils


def test_000():
    buf = DictBuffer(capacity=3)
    buf.push({"name": "Meeting 1", "start": "01.08.2025", "end": "03.08.2025", "description": "description 1", "location": "Room1"})
    buf.push({"name": "Meeting 2", "start": "04.08.2025", "end": "04.08.2025", "description": "description 2", "location": "Room2"})
    buf.push({"name": "Task 1", "start": "08.08.2025", "end": "10.08.2025", "description": "description 3", "location": "Outside"})
    
    a = ICalAction()
    a.ical_path = FileUtils.parent_folder(__file__) + os.sep + "test_ical.ics"
    a.name_key = "name"
    a.start_key = "start"
    a.end_key = "end"
    a.description_key = "description"
    a.location_key = "location"
    a.date_format = "%d.%m.%Y"
    
    a.buffer = buf
    
    a.execute()   