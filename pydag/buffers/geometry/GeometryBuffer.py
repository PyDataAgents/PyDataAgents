from dataclasses import dataclass, field
from pydag.buffers.DictBuffer import DictBuffer
from pydag.buffers.geometry.D3Geometry import D3Geometry


@dataclass
class GeometryBuffer(DictBuffer):
    
    resolution : list[int] = field(default_factory=list, metadata={"description": ""})
    
    def __post_init__(self):
        self._geometry : D3Geometry = None
    
    def _on_install(self, agent = None):
        super()._on_install(agent)
        x, y, z = self._geometry.create()