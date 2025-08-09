from dataclasses import dataclass, field
import json

import jsonpath_ng
from ...Action import Action
from ...BufferNode import BufferNode


@dataclass
class ReadJsonAction(BufferNode, Action):
    
    file_path : str = field(default=None, metadata={"description" : "path to the json file to read the data from"})
    json_path : str = field()
    
    def execute(self):
        with open(self.file_path) as json_data:
            d = json.loads(json_data)
            json_data.close()
        jsonpath_expression = jsonpath_ng.parse(d)
        matches = jsonpath_expression.find(json_data)
        self.buffer.push(matches)
        
    