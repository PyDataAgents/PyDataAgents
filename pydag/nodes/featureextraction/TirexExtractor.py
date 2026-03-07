from dataclasses import dataclass, field
from typing import Dict, Tuple
import os
import torch


from ...agents.Agent import Agent
from ...agents.AgentConfig import AgentConfig
from ..LearningNode import LearningNode


@dataclass
class TirexExtractor(LearningNode):
    """
    This `DataElement` represents a time series feature extraction model using the TiREx framework.
    Read: https://github.com/NX-AI/tirex
    for more information.
    """
    prediction_length: int = field(default=64, metadata={"description": "length of the prediction horizon"})
    output_keys : list[str] = field(default_factory=list, metadata={"description": "optional explicit output keys; if empty, default naming is used"})
    
    def __post_init__(self):
        super().__post_init__()
        self._models = None
        if torch.cuda.is_available():
            os.environ["TIREX_NO_CUDA"] = "0"
        else: 
            os.environ["TIREX_NO_CUDA"] = "1"
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        from tirex import load_model

        self._models = load_model("NX-AI/TiRex", device="cuda" if torch.cuda.is_available() else "cpu")
        
    def learn(self, data : dict, meta : dict = None) -> bool:
        return False
    
    def infer(self, data : dict, meta : dict = None) -> Tuple[Dict, Dict]:
        forecast = {}
        for key, d in data.items():
            x = torch.tensor(d)
            x_shape = x.shape
            x = x.view(-1, x.shape[-1])
            fc = self._models.forecast(context=x, prediction_length=self.prediction_length, output_type="numpy")[1] # mean - the output is flattened and converted to list
            for i in range(fc.shape[0]):
                if len(data.keys()) == len(self.output_keys):
                    forecast[self.output_keys[i]] = fc[i].tolist()  #convert to list
                else:
                    forecast[self.__class__.__name__ + "-" + AgentConfig.FEATURE + "-" + f"{i}"] = fc[i].tolist()  #convert to list
        return forecast, None
