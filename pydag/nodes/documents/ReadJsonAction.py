from dataclasses import dataclass, field
import json

import jsonpath_ng
from ...nodes.Action import Action
from ...nodes.BufferNode import BufferNode


@dataclass
class ReadJsonAction(BufferNode, Action):
    
    file_path : str = field(default=None, metadata={"description" : "path to the json file to read the data from"})
    json_path : str = field(default=None, metadata={"description": "json schema to parse the file for"})
    encoding : str = field(default="utf-8", metadata={"description": "name of the file encoding to use, e.g. utf-8 (default), utf-16, ..."})
    
    def _on_execute(self):
        with open(self.file_path, encoding=self.encoding) as f:
            d = json.loads(f.read())
            f.close()
        jsonpath_expression = jsonpath_ng.parse(self.json_path)
        matches = jsonpath_expression.find(d)
        self.add_data(matches)
        
    