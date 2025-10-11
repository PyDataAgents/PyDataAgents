from dataclasses import dataclass, field
from typing import Dict, Tuple
from chronos import ChronosPipeline, ChronosBoltPipeline
import torch
import os

from ...agents.Agent import Agent
from ..LearningElement import LearningElement
from ..DataElementConfig import DataElementConfig



@dataclass
class ChronosExtractor(LearningElement):

    """
    Chronos Extractor for time series data. Returns 384-dimensional embeddings for each input time series sample using a pretrained Chronos model.
    """
    
    model_name : str = field(default="amazon/chronos-bolt-mini", metadata={"description" : "name of available pretrained models, e.g. 'amazon/chronos-bolt-mini'. For further information look here: https://github.com/amazon-science/chronos-forecasting"})
    min_inference_samples : int = field(default=1, metadata={"description": "Number of Samples to do inference on."})

    def __post_init__(self):
        super().__post_init__()
        if torch.cuda.is_available():
            os.environ["TIREX_NO_CUDA"] = "0"
        else: 
            os.environ["TIREX_NO_CUDA"] = "1"
        self.learning_required = False # no learning required for pretrained models

    
    def install(self, agent : Agent = None):
        super().install(agent)    
        if "bolt" in self.model_name:
            self.model : ChronosBoltPipeline = ChronosBoltPipeline.from_pretrained(self.model_name,
                                                                       device_map="cuda" if torch.cuda.is_available() else "cpu",
                                                                       torch_dtype=torch.bfloat16)
        else:
            self.model : ChronosPipeline = ChronosPipeline.from_pretrained(self.model_name,
                                                                       device_map="cuda" if torch.cuda.is_available() else "cpu",
                                                                       torch_dtype=torch.bfloat16)

    def learn(self, data : dict, meta : dict) -> bool:
        return False
    
    def infer(self, data : dict, meta : dict) -> Tuple[Dict, Dict]:
        forecast = {}
        for i, key in enumerate(data.keys()):
            d = torch.tensor(data[key])
            embeddings, tokenizer_state = self.model.embed(d)
            embeddings = embeddings.mean(dim=1).view(-1)
            name = self.model_name.replace("/", "-")
            forecast[key + "-" + DataElementConfig.FEATURE + f"-{name}-{i}"] = embeddings.tolist()  #convert to list
        
        return forecast, None
    