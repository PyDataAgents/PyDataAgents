from dataclasses import dataclass
from ...BufferNode import BufferNode


@dataclass
class FFTTransform(BufferNode):

    def _on_execute(self):
        pass