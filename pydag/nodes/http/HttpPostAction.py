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
    """
    """
    
    url : str = field(default=None, metadata={"description": ""})
    headers : dict[str] = field(default=None, metadata={"description": "headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'}"})    
    timeout : float = field(default=10, metadata={"description": "timeout for requests"})
    json_path : str = field(default=None, metadata={"description": "JSONPath specififcation to parse the returned POST response"})
    
    def _on_execute(self):
        data = self.get_parent_data()
        json_obj = json.dumps(data)
        
        response = requests.post(self.url, headers=self.headers, timeout=self.timeout, json=json_obj)
        if response.status_code != 200:
            raise NodeException("Could not POST to " + self.url)
        d = response.json()     
        if self.json_path is not None:
            jsonpath_expression = jsonpath_ng.parse(self.json_path)
            json_obj = jsonpath_expression.find(d)
            if len(json_obj) == 1:
                json_obj = json_obj[0].value
            else:
                json_obj = [match.value for match in json_obj]
            self.add_data(json_obj)
        else:
            self.add_data(d)        
        