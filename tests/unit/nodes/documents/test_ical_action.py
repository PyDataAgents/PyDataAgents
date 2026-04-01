from datetime import datetime, timedelta
import os

import pytz
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.documents.ICalAction import ICalAction
from pydag.utils.FileUtils import FileUtils


def test_000():
    buf = DictBuffer(capacity=3)
    buf.install()
    d_now = datetime.now(pytz.UTC)
    d_1 = d_now
    d_2 = d_1 + timedelta(days=2)
    d_3 = d_now + timedelta(days=1)
    d_4 = d_3 + timedelta(days=1)
    d_5 = d_now + timedelta(days=4)
    d_6 = d_5 + timedelta(days=3)
        
    buf.push({"name": "Meeting 1", "start": f"{d_1.strftime('%Y-%m-%d')}", "end": f"{d_2.strftime('%Y-%m-%d')}", "description": "description 1", "location": "Room1"})
    buf.push({"name": "Meeting 2", "start": f"{d_3.strftime('%Y-%m-%d')}", "end": f"{d_4.strftime('%Y-%m-%d')}", "description": "description 2", "location": "Room2"})
    buf.push({"name": "Task 1", "start": f"{d_5.strftime('%Y-%m-%d')}", "end": f"{d_6.strftime('%Y-%m-%d')}", "description": "description 3", "location": "Outside"})
    
    print(buf.data())
    
    a = ICalAction()
    a.ical_path = FileUtils.parent_folder(__file__) + os.sep + "test_ical.ics"
    a.name_key = "name"
    a.start_key = "start"
    a.end_key = "end"
    a.description_key = "description"
    a.location_key = "location"
    a.date_format = "%Y-%m-%d"
    
    a.set_buffer(buf)
    a.install()
    
    a.execute()   
