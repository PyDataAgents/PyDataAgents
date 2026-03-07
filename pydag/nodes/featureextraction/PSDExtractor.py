from dataclasses import dataclass, field
from typing import Dict, Tuple
import torch
import os

from ...agents.Agent import Agent
from ..LearningNode import LearningNode
from ...agents.AgentConfig import AgentConfig
import numpy as np
from scipy.signal import welch



@dataclass
class PSDExtractor(LearningNode):

    """
    PSD for time series data. Returns 261-dimensional embeddings for each input time series sample using the Welch method from https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html.
    257 frequency bins + peak frequency + peak power + mean power + std power = 261 features per time series sample.
    """
    
    min_inference_samples : int = field(default=1, metadata={"description": "Number of Samples to do inference on."})
    output_keys : list[str] = field(default_factory=list, metadata={"description": "optional explicit output keys; if empty, default naming is used"})

    def __post_init__(self):
        super().__post_init__()
        self.learning_required = False # no learning required

    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)    
        self._models = welch
        
    def learn(self, data : dict, meta : dict) -> bool:
        return False
    
    def infer(self, data : dict, meta : dict) -> Tuple[Dict, Dict]:
        forecast = {}
        for i, key in enumerate(data.keys()):
            d = np.array(data[key])
            # Welch PSD
            f, Pxx = self._models(d,
                                fs = 1.0,
                                nperseg = 512,
                                nfft=512,
                                return_onesided=True)
            Pxx = Pxx.reshape(-1) # convert to numpy array and flatten - Stack all inference samples. It is similar to running n samples in sequence and adding them to the buffer.
            f = f.reshape(-1)
            if len(data.keys()) == len(self.output_keys):
                forecast[self.output_keys[i]] = Pxx.tolist()
            else:
                forecast[f"{self.cname()}-{AgentConfig.FEATURE}-{i}"] = Pxx.reshape(-1).tolist()  #convert to list

        return forecast, None
    
