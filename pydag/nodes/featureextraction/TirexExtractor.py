from dataclasses import dataclass, field
from typing import Dict, Tuple
import os
import torch
from tirex import load_model, ForecastModel


from ...agents.Agent import Agent
from ..DataElementConfig import DataElementConfig
from ..LearningElement import LearningElement


@dataclass
class TirexExtractor(LearningElement):
    """
    This `DataElement` represents a time series feature extraction model using the TiREx framework.
    Read: https://github.com/NX-AI/tirex
    for more information.
    """
    prediction_length: int = field(default=64, metadata={"description": "length of the prediction horizon"})
    
    def __post_init__(self):
        super().__post_init__()
        self.model = None
        if torch.cuda.is_available():
            os.environ["TIREX_NO_CUDA"] = "0"
        else: 
            os.environ["TIREX_NO_CUDA"] = "1"
        
    def install(self, agent : Agent = None):
        super().install(agent)
        self.model : ForecastModel = load_model("NX-AI/TiRex", device="cuda" if torch.cuda.is_available() else "cpu")
        
    def learn(self, data : dict, meta : dict = None) -> bool:
        return False
    
    def infer(self, data : dict, meta : dict = None) -> Tuple[Dict, Dict]:
        forecast = {}
        for key, d in data.items():
            x = torch.tensor(d)
            x_shape = x.shape
            x = x.view(-1, x.shape[-1])
            fc = self.model.forecast(context=x, prediction_length=self.prediction_length, output_type="numpy")[1] # mean - the output is flattened and converted to list
            for i in range(fc.shape[0]):
                forecast[key + "-" + DataElementConfig.FEATURE + f"-Tirex-{i}"] = fc[i].tolist()  #convert to list
        
        return forecast, None