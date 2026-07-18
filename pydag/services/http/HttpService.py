from dataclasses import dataclass, field
import json
import jsonpath_ng
import urllib3

from ..MappingService import MappingService
from ..ServiceException import ServiceException
from ..WriteService import WriteService
from ..ReadService import ReadService
from ...agents.Agent import Agent
from ...buffers.ListBuffer import ListBuffer
from ...buffers.DictBuffer import DictBuffer
from ...buffers.Buffer import Buffer

@dataclass
class HttpService(ReadService, WriteService):
    """`MappingService` for reading and writing data from/to http endpoints
    """
    
    base_url : str = field(default=None, metadata={"description": "base URL for the HTTP requests, e.g. http://localhost:8080/api"})
    headers : dict[str] = field(default=None, metadata={"description": "headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'}"})
    json_path : bool = field(default=False, metadata={"description": "if True, the response data is expected to be in JSON format and will be parsed accordingly to specification in address"})
    
    def __post_init__(self):
        super().__post_init__()
        self._http : urllib3.PoolManager = None
    
    def _on_install(self, agent : Agent = None):        
        super()._on_install(agent)
        self._http = urllib3.PoolManager()
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        self._http = None
        
    def read_from_source(self):
        if len(self.addresses) == 0 and len(self.get_buffers()) == 1:
            buffer : Buffer = next(iter(self.get_buffers().values()))
            if self.headers is None:
                response = self._http.request("GET", self.base_url)
            else:
                response = self._http.request("GET", self.base_url, headers = self.headers)
            body = response.data
            s = body.decode("utf-8")
            if self.json_path:
                json_data = json.loads(s)
                jsonpath_expression = jsonpath_ng.parse(self.json_path)
                matches = jsonpath_expression.find(json_data)
                dic = {}
                for match in matches:
                    path = ".".join(match.path.fields)
                    dic[path] = match.value
                buffer.push(dic)
            else:
                if isinstance(buffer, DictBuffer):
                    dic = json.loads(s)
                    buffer.push(dic)    
                elif isinstance(buffer, ListBuffer):
                    buffer.push(s)            
        elif len(self.get_buffers()) == len(self.addresses):
            if self.json_path:
                b = 0
                for buffer in self.get_buffers().values():
                    d_address = MappingService.address_to_dict(self.addresses[b])
                    if "json_path" not in d_address:
                        raise ServiceException("json_path must be specified in address when json_path is True")
                    elif "url" not in d_address:
                        raise ServiceException("url must be specified in address when json_path is True")
                    else:
                        json_path = d_address["json_path"]
                        url = d_address["url"]
                        if self.base_url is not None:
                            url : str = self.base_url + url
                        if self.headers is None:
                            response = self._http.request("GET", url)
                        else:
                            response = self._http.request("GET", url, headers = self.headers)
                        val = response.data
                        json_data = json.loads(val)
                        jsonpath_expression = jsonpath_ng.parse(json_path)
                        matches = jsonpath_expression.find(json_data)
                        buffer.push(matches)
                        b = b + 1
            else:
                b = 0
                for buffer in self.get_buffers().values():
                    if self.base_url is None:
                        url : str = self.addresses[b]
                    else:
                        url : str = self.base_url + self.addresses[b]
                    if self.headers is None:
                        response = self._http.request("GET", url)
                    else:
                        response = self._http.request("GET", url, headers = self.headers)
                    val = response.data
                    buffer.push(val)
                    b = b + 1
        else:
            raise ServiceException("size of buffers and addresses must match")
            
    def write_to_sink(self):
        if len(self.get_buffers()) != len(self.addresses):
            raise ServiceException("size of buffers and addresses must match")
        b = 0
        for buffer in self.get_buffers().values():
            val = buffer.data(n = self.n, persistent = self.persistent)
            if len(val) > 1:
                # TODO
                raise ServiceException("writing more than one value is not supported yet")
            else:
                if self.base_url is None:
                    url : str = self.addresses[b]
                else:
                    url : str = self.base_url + self.addresses[b]
                if self.headers is None:
                    self._http.request("POST", url, body=val[0])
                else:
                    self._http.request("POST", url, body=val[0], headers = self.headers)
            b = b + 1
        
