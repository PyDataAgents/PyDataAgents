from pydag.buffers.DictBuffer import DictBuffer
from pydag.statemachine.actions.documents.ICalAction import ICalAction


def test_000():
    buf = DictBuffer()
    
    a = ICalAction()
    a.ical_path = ""
    a.name_key = ""
    a.start_key = ""
    a.end_key = ""
    a.description_key = ""
    a.location_key = ""
    a.date_format = ""
    
    a.buffer = buf
    
    a.execute()   