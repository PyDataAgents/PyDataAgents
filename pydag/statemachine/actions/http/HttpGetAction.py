from dataclasses import dataclass, field
import jsonpath_ng

import requests
from ...Action import Action
from ...BufferNode import BufferNode


@dataclass
class HttpGetAction(BufferNode, Action):
    
    url : str = field(default=None, metadata={"description": "url for HTTP GET method"})
    headers : dict[str] = field(default=None, metadata={"description": "headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'}"})    
    timeout : float = field(default=10, metadata={"description": "timeout for requests"})
    json_path : str = field(default=None, metadata={"description": "JSONPath specififcation to parse or access the data in buffer"})
    
    def execute(self):
        response = requests.get(self.url, headers=self.headers, timeout=self.timeout)
        data = response.json()
        if self.json_path is not None:
            jsonpath_expression = jsonpath_ng.parse(self.json_path)
            data = jsonpath_expression.find(data)
            if len(data) == 1:
                data = data[0].value
            else:
                data = [match.value for match in data]
        self.buffer.push(data)