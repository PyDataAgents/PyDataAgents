import os
import time

from pydag.nodes.BufferNode import BufferNode
from pydag.nodes.Action import Action


def touch(path: str, content: str = "") -> None:
    """Create or overwrite a text file and wait briefly so filesystem events fire."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    # small pause so watchdog can pick up the event
    time.sleep(0.05)


class CollectBufferAction(BufferNode, Action):
    """Test helper action that simply records all buffers it receives."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.collected: list[dict] = []

    def _on_execute(self):
        self.collected.append(self.get_parent_data())
