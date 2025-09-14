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
        with open(self.file_path) as f:
            d = json.loads(f.read())
            f.close()
        jsonpath_expression = jsonpath_ng.parse(self.json_path)
        matches = jsonpath_expression.find(d)
        self.buffer.push(matches)
        
    