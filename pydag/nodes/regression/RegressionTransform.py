from dataclasses import dataclass, field
from typing import Dict, Tuple
import os
import numpy as np
from tirex import load_model, ForecastModel
import torch
from sktime.forecasting.chronos import ChronosForecaster
from sktime.forecasting.base import ForecastingHorizon


from ...utils.DataUtils import DataUtils
from ...agents.Agent import Agent
from ..LearningNode import LearningNode
from ...agents.AgentConfig import AgentConfig


@dataclass
class RegressionTransform(LearningNode):
    """Code Service to do Regression on Inputs
    """

    model_name : str = field(default="Tirex", metadata={"description": "name of the model to use for regression. Default is Tirex"})
    prediction_length: int = field(default=64, metadata={"description": "length of the prediction horizon"})
    output_keys : list[str] = field(default_factory=list, metadata={"description": "optional explicit output keys; if empty, default naming is used"})

    def __post_init__(self):
        super().__post_init__()
        self._models: ForecastModel = None
        if torch.cuda.is_available():
                print(torch.cuda.get_device_name(0))
                os.environ["TIREX_NO_CUDA"] = "0"
        else: 
            print("No GPU available")
            os.environ["TIREX_NO_CUDA"] = "1"

    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if self.model_name == "Tirex":
            self._models = load_model("NX-AI/TiRex", device="cuda" if torch.cuda.is_available() else "cpu")
        elif self.model_name == "CHRONOS":
            self._models : ChronosForecaster = ChronosForecaster(model_path="amazon/chronos-t5-tiny")

    def learn(self, data : dict, meta : dict = None) -> bool:
            self.learning_required = False
          
    def infer(self, data : dict, meta : dict = None) -> Tuple[Dict, Dict]:
        if self.model_name == "Tirex":
            forecast = {}
            for key, d in data.items():
                x = torch.tensor(d)
                x_shape = x.shape
                x = x.view(-1, x.shape[-1])
                fc = self._models.forecast(context=x, prediction_length=self.prediction_length, output_type="numpy")[1] # mean
                for i in range(fc.shape[0]):
                    forecast[self.__class__.__name__ + "-" + AgentConfig.FEATURE + "-" + f"{i}"] = fc[i].tolist()  #convert to list
            return forecast, None
        

        elif self.model_name == "CHRONOS":
            forecast = {}
            np_data = DataUtils.dict_to_ndarray(data)
            data_len = np_data.shape[-1] # Assuming the last dimension is the time dimension
            fh = ForecastingHorizon(np.arange(data_len, data_len+self.prediction_length), is_relative=False)
            for i, key in enumerate(data.keys()):
                self._models.fit(y=np_data[i], fh=fh)
                y_pred = self._models.predict()
                forecast[key + "-" + AgentConfig.FEATURE + f"-{self.model_name}-{i}"] = y_pred.tolist()  #convert to list
            return forecast, None

    


            
