from dataclasses import dataclass, field
import json
import jsonpath_ng
import urllib3
from PyDataGrabber.pydatagrabber.adapters.AdapterException import AdapterException
from PyDataGrabber.pydatagrabber.adapters.ReadAdapter import ReadAdapter
from PyDataGrabber.pydatagrabber.adapters.WriteAdapter import WriteAdapter
from PyDataGrabber.pydatagrabber.buffers.Buffer import Buffer
from PyDataGrabber.pydatagrabber.utils.AdapterUtils import AdapterUtils

@dataclass
class HttpAdapter(ReadAdapter, WriteAdapter):
    """Adapter for reading and writing data from/to http endpoints
    """
    
    base_url : str = field(default=None, metadata={"description": "base URL for the HTTP requests, e.g. http://localhost:8080/api"})
    headers : dict[str] = field(default=None, metadata={"description": "headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'}"})
    json_path : bool = field(default=False, metadata={"description": "if True, the response data is expected to be in JSON format and will be parsed accordingly to specification in address"})
    
    def __init__(self):
        super().__init__()
        self.http : urllib3.PoolManager = None
        
    def connect(self) -> bool:
        self.http = urllib3.PoolManager()
        return True
    
    def disconnect(self):
        self.http = None
        return True
    
    def read_from_source(self, buffers: dict[str, Buffer], addresses: list[str], n: int = 1):
        if len(addresses) == 0 and len(buffers) == 1:
            buffer : Buffer = buffers.values()[0]
            if self.headers is None:
                response = self.http.request("GET", self.base_url)
            else:
                response = self.http.request("GET", self.base_url, headers = self.headers)
            val = response.data
            buffer.push(val)
            
        elif len(buffers) == len(addresses):
            if self.json_path:
                b = 0
                for buffer in buffers.values():
                    d_address = AdapterUtils.address_to_dict(addresses[b])
                    if "json_path" not in d_address:
                        raise AdapterException("json_path must be specified in address when json_path is True")
                    elif "url" not in d_address:
                        raise AdapterException("url must be specified in address when json_path is True")
                    else:
                        json_path = d_address["json_path"]
                        url = d_address["url"]
                        if self.base_url is not None:
                            url : str = self.base_url + url
                        if self.headers is None:
                            response = self.http.request("GET", url)
                        else:
                            response = self.http.request("GET", url, headers = self.headers)
                        val = response.data
                        json_data = json.loads(val)
                        jsonpath_expression = jsonpath_ng.parse(json_path)
                        matches = jsonpath_expression.find(json_data)
                        buffer.push(matches)
                        b = b + 1
            else:
                b = 0
                for buffer in buffers.values():
                    if self.base_url is None:
                        url : str = addresses[b]
                    else:
                        url : str = self.base_url + addresses[b]
                    if self.headers is None:
                        response = self.http.request("GET", url)
                    else:
                        response = self.http.request("GET", url, headers = self.headers)
                    val = response.data
                    buffer.push(val)
                    b = b + 1
        else:
            raise AdapterException("size of buffers and addresses must match")
            
    def write_to_sink(self, buffers: dict[str, Buffer], addresses: list[str], n: int = 1, persistent: bool = True):
        if len(buffers) != len(addresses):
            raise AdapterException("size of buffers and addresses must match")
        b = 0
        for buffer in buffers.values():
            val = buffer.data(n, persistent)
            if len(val) > 1:
                # TODO
                raise AdapterException("writing more than one value is not supported yet")
            else:
                if self.base_url is None:
                    url : str = addresses[b]
                else:
                    url : str = self.base_url + addresses[b]
                if self.headers is None:
                    self.http.request("POST", url, body=val[0])
                else:
                    self.http.request("POST", url, body=val[0], headers = self.headers)
            b = b + 1
        
