from dataclasses import dataclass, field
from typing import Dict, Tuple
import os
import numpy as np
import torch


from ...agents.Agent import Agent
from ..LearningNode import LearningNode
from ...agents.AgentKeywords import AgentKeywords


@dataclass
class RegressionTransform(LearningNode):
    """Code Service to do Regression on Inputs
    """

    model_name : str = field(default="Tirex", metadata={"description": "name of the model to use for regression. Default is Tirex"})
    learning_required : bool = field(default=True, metadata={"description": "whether the model requires a learning phase before inference"})
    prediction_length: int = field(default=64, metadata={"description": "length of the prediction horizon"})
    output_keys : list[str] = field(default_factory=list, metadata={"description": "optional explicit output keys; if empty, default naming is used"})

    def __post_init__(self):
        super().__post_init__()
        self._models = None
        self._requires_learning = bool(self.learning_required)
        if torch.cuda.is_available():
                print(torch.cuda.get_device_name(0))
                os.environ["TIREX_NO_CUDA"] = "0"
        else: 
            print("No GPU available")
            os.environ["TIREX_NO_CUDA"] = "1"

    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if self.model_name == "Tirex":
            from tirex import load_model

            self._models = load_model("NX-AI/TiRex", device="cuda" if torch.cuda.is_available() else "cpu")
        elif self.model_name == "CHRONOS":
            from chronos import ChronosPipeline

            self._models = ChronosPipeline.from_pretrained(
                "amazon/chronos-t5-tiny",
                device_map="cuda" if torch.cuda.is_available() else "cpu",
                torch_dtype=torch.bfloat16,
            )

    def learn(self, data : dict, meta : dict = None) -> bool:
            self._requires_learning = False
            return False

    def _forecast_key(self, index: int, output_count: int, default_key: str | None = None) -> str:
        if len(self.output_keys) == output_count:
            return self.output_keys[index]
        if default_key is not None:
            return default_key
        return f"{self.cname()}-{AgentKeywords.FEATURE}-{index}"
          
    def infer(self, data : dict, meta : dict = None) -> Tuple[Dict, Dict]:
        if self.model_name == "Tirex":
            forecast = {}
            forecast_index = 0
            for d in data.values():
                x = torch.as_tensor(d, dtype=torch.float32)
                x = x.view(-1, x.shape[-1])
                _, fc = self._models.forecast(
                    context=x,
                    prediction_length=self.prediction_length,
                    output_type="torch",
                )
                for row in fc:
                    forecast[self._forecast_key(forecast_index, len(data))] = row.reshape(-1).cpu().tolist()
                    forecast_index += 1
            return forecast, None


        elif self.model_name == "CHRONOS":
            forecast = {}
            for i, key in enumerate(data.keys()):
                context = torch.tensor(np.asarray(data[key]), dtype=torch.float32).view(1, -1)
                y_pred = self._models.predict(
                    context=context,
                    prediction_length=self.prediction_length,
                    limit_prediction_length=False,
                )
                if isinstance(y_pred, torch.Tensor):
                    # Chronos returns samples; reduce to a single forecast vector.
                    if y_pred.ndim >= 3:
                        y_pred = y_pred.mean(dim=1)
                    y_pred = y_pred.reshape(-1).cpu().tolist()
                else:
                    y_pred = np.asarray(y_pred).reshape(-1).tolist()
                forecast[self._forecast_key(i, len(data), f"{key}-{AgentKeywords.FEATURE}-{self.model_name}-{i}")] = y_pred
            return forecast, None

    


            
