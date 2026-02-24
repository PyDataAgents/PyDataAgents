from pydag.adapters.http.HttpAdapter import HttpAdapter
from pydag.buffers.DataType import DataType
from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.ListBuffer import ListBuffer


def test_config_options():
    ha = HttpAdapter()
    print(ha.config_options())
    
def test_single_listbuffer():
    ha = HttpAdapter(base_url="https://postman-echo.com/get")
    ha.install()
    
    buf = ListBuffer(capacity=1, data_type=DataType.STRING.value)
    buf.install()
    
    buffers = buf.to_dict()
    addresses = []
    
    if ha.connect():
        ha.read_from_source(buffers, addresses)
    
        data = buf.data()
        print(data)
        
        if len(data['values']) != 1:
            assert False, "Data length incorrect"
    else:
        assert False, "Could not connect to HTTP source"
        
def test_single_dictbuffer():
    ha = HttpAdapter(base_url="https://postman-echo.com/get")
    ha.install()
    
    buf = DictBuffer(capacity=1, data_type=DataType.STRING.value)
    buf.install()
    
    buffers = buf.to_dict()
    addresses = []
    
    if ha.connect():
        ha.read_from_source(buffers, addresses)
    
        data = buf.data()
        print(data)
        
        if len(data.keys()) != 3:
            assert False, "key length is incorrect"
    else:
        assert False, "Could not connect to HTTP source"
        
def test_single_listbuffer_with_jsonpath():
    ha = HttpAdapter(base_url="https://postman-echo.com/get", json_path="$.headers.host")
    ha.install()
    
    buf = ListBuffer(capacity=1, data_type=DataType.STRING.value)
    buf.install()
    
    buffers = buf.to_dict()
    addresses = []
    
    if ha.connect():
        ha.read_from_source(buffers, addresses)
    
        data = buf.data()
        print(data)
        
        if data['values'][0] != "postman-echo.com":
            assert False, "extracted json content is incorrect"
    else:
        assert False, "Could not connect to HTTP source"
        
def test_single_dictbuffer_with_jsonpath():
    ha = HttpAdapter(base_url="https://postman-echo.com/get", json_path="$.headers.host")
    ha.install()
    
    buf = DictBuffer(capacity=1, data_type=DataType.STRING.value)
    buf.install()
    
    buffers = buf.to_dict()
    addresses = []
    
    if ha.connect():
        ha.read_from_source(buffers, addresses)
    
        data = buf.data()
        print(data)
        
        if data['host'][0] != "postman-echo.com":
            assert False, "extracted json content is incorrect"
    else:
        assert False, "Could not connect to HTTP source"
        
        
def test_addresses():
    # TODO
    pass