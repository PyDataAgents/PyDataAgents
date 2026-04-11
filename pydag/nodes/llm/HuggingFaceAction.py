from dataclasses import dataclass, field
import json
from transformers import pipeline
from transformers.pipelines import PIPELINE_REGISTRY


from ...utils.DataUtils import DataUtils
from ..NodeException import NodeException
from ..Action import Action
from ..BufferNode import BufferNode
from ...agents.Agent import Agent


@dataclass
class HuggingFaceAction(BufferNode, Action):
    
    task : str = field(default=None, metadata={"description": "task category of the model to use, e.g. image-classification, text-generation, sentiment-analysis, ... execute HuggingFaceNode.tasklist for full list"})
    model : str = field(default=None, metadata={"description": ""})
    ignore_keys : list[str] = field(default_factory=lambda: ["index", "timestamps"], metadata={"description": "list of keys to ignore when extracting from parent buffers, ignore_keys are applied after input_keys"})
            
    def __post_init__(self):
        super().__post_init__()
        self._pipeline = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if self.task is None:
            raise NodeException(f"No task was specified in {self.__class__.__name__} {self.id}")
        self._pipeline = pipeline(task=self.task, model=self.model)
    
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        self._pipeline = None
        
    def _on_execute(self):
        data = self.get_parent_data(by_rows = True)
        use_output_keys : bool = False       
        i : int
        new_data : dict = {}       
        dic : dict
        for dic in data:
            i = 0
            new_data = {}
            for k, v in dic.items():
                use_output_keys = False
                if len(self.output_keys) > 0 and len(self.output_keys) == len(dic):
                    use_output_keys = True
                d = self._pipeline(v)
                list_output : bool = False
                if isinstance(d, list):
                    first = d[0]
                    if isinstance(first, dict):
                        if len(first) == 1:
                            list_output = True
                if list_output:
                    if len(d) == 1:
                        d = list(first.values())
                    else:
                        values : list = []
                        it : dict
                        for it in d:
                            values.append(list(it.values()))
                        d = values
                else:
                    d = json.dumps(d)
                if use_output_keys:
                    new_data[self.output_keys[i]] = d
                else:
                    new_data[k] = d
                i = i + 1
            self.add_data(new_data)
    
    @staticmethod
    def task_list() -> list[str]:
        return PIPELINE_REGISTRY.get_supported_tasks()
    