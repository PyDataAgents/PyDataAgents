from pydag.buffers.DataType import DataType
from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.ListBuffer import ListBuffer
from pydag.services.ThreadType import ThreadType
from pydag.services.MappingType import MappingType
from pydag.services.http.HttpService import HttpService


def test_config_options():
    ha = HttpService()
    print(ha.config_options())
    
def test_single_listbuffer():
    buf = ListBuffer(capacity=1, data_type=DataType.STRING.value)
    buf.install()
    
    ha = HttpService(base_url="https://postman-echo.com/get", thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.READ.value)
    ha.add_buffer(buf)
    ha.install()
            
    ha._read_from_source()
    
    data = buf.data()
    print(data)
        
    if len(data['values']) != 1:
        assert False, "Data length incorrect"
        
        
def test_single_dictbuffer():
    buf = DictBuffer(capacity=1, data_type=DataType.STRING.value)
    buf.install()
    ha = HttpService(base_url="https://postman-echo.com/get", thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.READ.value)
    ha.add_buffer(buf)
    ha.install()
    
    ha._read_from_source()
    
    data = buf.data()
    print(data)
        
    if len(data.keys()) != 3:
        assert False, "key length is incorrect"
        
def test_single_listbuffer_with_jsonpath():
    buf = ListBuffer(capacity=1, data_type=DataType.STRING.value)
    buf.install()
    ha = HttpService(base_url="https://postman-echo.com/get", json_path="$.headers.host", thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.READ.value)
    ha.add_buffer(buf)
    ha.install()
    
    ha._read_from_source()
    
    data = buf.data()
    print(data)
        
    if data['values'][0] != "postman-echo.com":
        assert False, "extracted json content is incorrect"
        
def test_single_dictbuffer_with_jsonpath():
    buf = DictBuffer(capacity=1, data_type=DataType.STRING.value)
    buf.install()
    ha = HttpService(base_url="https://postman-echo.com/get", json_path="$.headers.host", thread_type=ThreadType.MILLI_SECOND.value, mapping_type=MappingType.READ.value)
    ha.add_buffer(buf)
    ha.install()
       
    ha._read_from_source()
    data = buf.data()
    print(data)
        
    if data['host'][0] != "postman-echo.com":
        assert False, "extracted json content is incorrect"