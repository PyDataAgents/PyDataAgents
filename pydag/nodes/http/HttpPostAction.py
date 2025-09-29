from dataclasses import dataclass, field
import json
from loguru import logger
import jsonpath_ng
import requests

from ..NodeException import NodeException
from ..Action import Action
from ..BufferNode import BufferNode


@dataclass
class HttpPostAction(BufferNode, Action):
    
    url : str = field(default=None, metadata={"description": ""})
    headers : dict[str] = field(default=None, metadata={"description": "headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'}"})    
    timeout : float = field(default=10, metadata={"description": "timeout for requests"})
    json_path : str = field(default=None, metadata={"description": "JSONPath specififcation to parse or access the data in buffer"})
    persistent : bool = field(default=False, metadata={"description": "specifies whether data is removed from buffer after access"})
    n : int = field(default=1, metadata={"description": "specifies the number of samples to remove from buffer, n=0 -> all"})
    
    def execute(self):
        data = self.buffer.data(n=self.n, persistent=self.persistent)
        json_obj = json.dumps(data)
        if self.json_path is not None:
            jsonpath_expression = jsonpath_ng.parse(self.json_path)
            json_obj = jsonpath_expression.find(json_obj)
            if len(json_obj) == 1:
                json_obj = json_obj[0].value
            else:
                json_obj = [match.value for match in json_obj]
        response = requests.post(self.url, headers=self.headers, timeout=self.timeout, json=json_obj)
        if response.status_code != 200:
            raise NodeException("Could not POST to " + self.url)
        logger.info(response.json())