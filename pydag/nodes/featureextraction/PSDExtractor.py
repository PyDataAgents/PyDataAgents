from dataclasses import dataclass, field
from typing import Dict, Tuple
from chronos import ChronosPipeline, ChronosBoltPipeline
import torch
import os

from ...agents.Agent import Agent
from ..LearningElement import LearningElement
from ..DataElementConfig import DataElementConfig
import numpy as np
from scipy.signal import welch



@dataclass
class PSDExtractor(LearningElement):

    """
    PSD for time series data. Returns 261-dimensional embeddings for each input time series sample using the Welch method from https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html.
    257 frequency bins + peak frequency + peak power + mean power + std power = 261 features per time series sample.
    """
    
    min_inference_samples : int = field(default=1, metadata={"description": "Number of Samples to do inference on."})

    def __post_init__(self):
        super().__post_init__()
        self.learning_required = False # no learning required

    
    def install(self, agent : Agent = None):
        super().install(agent)    
        self.model = welch
    def learn(self, data : dict, meta : dict) -> bool:
        return False
    
    def infer(self, data : dict, meta : dict) -> Tuple[Dict, Dict]:
        forecast = {}
        for i, key in enumerate(data.keys()):
            d = np.array(data[key])
            # Welch PSD
            f, Pxx = self.model(d,
                                fs = 1.0,
                                nperseg = 512,
                                nfft=512,
                                return_onesided=True)
            forecast[key + "-" + DataElementConfig.FEATURE + f"-welch-{i}"] = Pxx.reshape(-1).tolist()  #convert to list

        return forecast, None
    