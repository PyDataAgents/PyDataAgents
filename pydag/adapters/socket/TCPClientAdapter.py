from dataclasses import dataclass
from ...adapters.WriteAdapter import WriteAdapter
from ...adapters.ReadAdapter import ReadAdapter


@dataclass
class TCPClientAdapter(ReadAdapter, WriteAdapter):
    
    
    
    pass