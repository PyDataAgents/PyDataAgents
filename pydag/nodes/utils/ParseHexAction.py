from dataclasses import dataclass, field
import struct

from pydag.agents.Agent import Agent
from pydag.nodes.Action import Action
from pydag.nodes.BufferNode import BufferNode
from pydag.nodes.NodeException import NodeException

@dataclass
class ParseHexAction(BufferNode, Action):
    """ 
    A node that parses a hexadecimal string into fixed data schema.
    Data is expected to be in the form of a dictionary with string values representing hexadecimal numbers.
    The schema defines how to unpack the hex string into Python data types, and scaling factors can be applied to each field after unpacking.
    The output keys define the names of the fields in the output data and must adhere to the same length as the schema.
    
    Available schema datatypes:
    - 'B': unsigned char
    - 'b': signed char
    - 'H': unsigned short
    - 'h': signed short
    - 'I': unsigned int
    - 'i': signed int
    - 'f': float
    - 'd': double

    with '>' for big-endian, '<' for little-endian, and '!' for network byte order.

    """
    
    schema : str = field(default=None, metadata={"description": "The schema to parse the hex string into"})
    scaling : list[float] = field(default_factory=list, metadata={"description": "Scaling factors for each field in the schema, specify empty list (default) or None for no scaling"})
    
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if self.schema is None:
            raise NodeException("ParseHexAction requires a schema to be specified")
        if len(self.scaling) > 0 and len(self.scaling) != len(self.output_keys):
            raise NodeException(f"Scaling factors length {len(self.scaling)} does not match output keys length {len(self.output_keys)}")
        
    def _on_execute(self):
        data = self.get_parent_data(by_rows=True)
        row : dict
        new_row : dict
        for row in data:
            for k, v in row.items():
                if isinstance(v, str):
                    hx : str = v.strip()                
                    up = struct.unpack(self.schema, bytes.fromhex(hx))
                    if len(up) != len(self.output_keys):
                        raise NodeException(f"Parsed data length {len(up)} does not match output keys length {len(self.output_keys)}")
                    if len(self.scaling) > 0:
                        up = [up[i] * self.scaling[i] if self.scaling[i] is not None else up[i] for i in range(len(up))]
                    new_row = {}
                    for i, key in enumerate(self.output_keys):
                        new_row[key] = up[i]
                    if len(new_row) > 0:
                        self.add_data(new_row)