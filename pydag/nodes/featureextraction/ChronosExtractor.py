from dataclasses import dataclass, field
from typing import Dict, Tuple
from chronos import ChronosPipeline, ChronosBoltPipeline
import torch
import os

from ...agents.Agent import Agent
from ..LearningNode import LearningNode
from ...agents.AgentConfig import AgentConfig



@dataclass
class ChronosExtractor(LearningNode):

    """
    Chronos Extractor for time series data. Returns 384-dimensional embeddings for each input time series sample using a pretrained Chronos model.
    """
    
    model_name : str = field(default="amazon/chronos-bolt-mini", metadata={"description" : "name of available pretrained models, e.g. 'amazon/chronos-bolt-mini'. For further information look here: https://github.com/amazon-science/chronos-forecasting"})
    min_inference_samples : int = field(default=1, metadata={"description": "Number of Samples to do inference on."})
    output_keys : list[str] = field(default_factory=list, metadata={"description": "optional explicit output keys; if empty, default naming is used"})
    
    def __post_init__(self):
        super().__post_init__()
        if torch.cuda.is_available():
            os.environ["TIREX_NO_CUDA"] = "0"
        else: 
            os.environ["TIREX_NO_CUDA"] = "1"
        self.learning_required = False # no learning required for pretrained models

    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)    
        if "bolt" in self.model_name:
            self._models : ChronosBoltPipeline = ChronosBoltPipeline.from_pretrained(self.model_name,
                                                                       device_map="cuda" if torch.cuda.is_available() else "cpu",
                                                                       torch_dtype=torch.bfloat16)
        else:
            self._models : ChronosPipeline = ChronosPipeline.from_pretrained(self.model_name,
                                                                       device_map="cuda" if torch.cuda.is_available() else "cpu",
                                                                       torch_dtype=torch.bfloat16)

    def learn(self, data : dict, meta : dict) -> bool:
        return False
    
    def infer(self, data : dict, meta : dict) -> Tuple[Dict, Dict]:
        forecast = {}
        for i, key in enumerate(data.keys()):
            d = torch.tensor(data[key])
            embeddings, tokenizer_state = self._models.embed(d)
            embeddings = embeddings.mean(dim=1).view(-1)
            #name = self.model_name.replace("/", "-")
            if len(data.keys()) == len(self.output_keys):
                forecast[self.output_keys[i]] = embeddings.tolist()  #convert to list
            else:
                forecast[self.__class__.__name__ + "-" + AgentConfig.FEATURE + "-" + f"{i}"] = embeddings.tolist()  #convert to list
        
        return forecast, None
    