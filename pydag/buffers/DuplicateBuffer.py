from dataclasses import dataclass, field

from ..buffers.DictBuffer import DictBuffer
from .Buffer import Buffer
from ..agents.Agent import Agent


@dataclass
class DuplicateBuffer(DictBuffer):
    """ `Buffer` that pushes all its inserted data to specified other buffers as well.
    """
    
    duplicate_ids : list = field(default_factory = list, metadata={"description", "id's of the other buffers used for duplicating the data"})
    
    def __post_init__(self):
        super().__post_init__()
        self.duplicates : dict[str, Buffer] = {}

    def install(self, agent : Agent = None):
        super().install(agent)
        if self.duplicates is not None:
            self.duplicate_ids = list(self.duplicates.keys())
        elif len(self.duplicate_ids) > 0:
            for di in self.duplicate_ids:
                if agent is None:
                    buf = DictBuffer(
                        id = di,
                        load_on_install=self.load_on_install,
                        capacity=self.capacity,
                        data_type=self.data_type,
                        initial_values=self.initial_values,
                        unit=self.unit,
                        description=self.description,
                        timestamps_enabled=self.timestamps_enabled,
                        timestamps_key=self.timestamps_key,
                        index_enabled=self.index_enabled,
                        index_key=self.index_key
                    )
                    buf.install()                
                    self.duplicates[buf.id] = buf
                else:
                    if di in agent.buffer_store:
                        self.duplicates[di] = agent.buffer_store.get(di)
                    else:
                        buf = DictBuffer(
                            id = di,
                            load_on_install=self.load_on_install,
                            capacity=self.capacity,
                            data_type=self.data_type,
                            initial_values=self.initial_values,
                            unit=self.unit,
                            description=self.description,
                            timestamps_enabled=self.timestamps_enabled,
                            timestamps_key=self.timestamps_key,
                            index_enabled=self.index_enabled,
                            index_key=self.index_key
                        )
                        buf.install()                
                        self.duplicates[buf.id] = buf
                        agent.add_buffer(buf)
        
    def uninstall(self, agent : Agent = None):
        super().uninstall(agent)
        for buf in self.duplicates.values():
            buf.uninstall()        

    def push(self, elements: list | dict):
        super().push(elements)
        for buf in self.duplicates.values():
            buf.push(elements)
           
    def clear(self):
        self.elements.clear()
        for buf in self.duplicates.values():
            buf.clear()