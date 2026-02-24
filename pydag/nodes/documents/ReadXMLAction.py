from dataclasses import dataclass, field
import lxml
from lxml import etree

from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.NodeException import NodeException


from ...nodes.Action import Action
from ...nodes.BufferNode import BufferNode


@dataclass
class ReadXMLAction(BufferNode, Action):
    
    file_path : str = field(default=None, metadata={"description" : "path to the xml file to read the data from"})
    xpath : str = field(default=None, metadata={"description": "xml xpath schema to parse the file for"})
    
    def _on_execute(self):
        # Load XML from file
        tree : etree = etree.parse(self.file_path)
        
        # Get the root element
        #root = tree.getroot()
        
        # Get xpath data
        d = tree.xpath(self.xpath)
        # force Elements to dict
        if isinstance(d[0], lxml.etree._Element):
            dic = {} 
            for elem in d:
                if elem.tag in dic:
                    dic[elem.tag].append(elem.text)
                else:
                    dic[elem.tag] = [elem.text]
            self.add_data(dic)                
        elif issubclass(self._buffer.__class__, DictBuffer) or isinstance(self._buffer, DictBuffer):
            dic : dict = {}
            if len(self.output_keys) == 0:
                dic = {"values" : d}
                self.add_data(dic)
            elif len(self.output_keys) == 1:
                dic = {self.output_keys[0]: d}
                self.add_data(dic)
            else:
                raise NodeException(f"only 1 output_key is needed for {BufferNode.cname()}: {self.config_options()}")  
        else:
            self.add_data(d)
        
    