from dataclasses import dataclass, field
from typing import Dict, Tuple
from sktime.transformations.panel.rocket import Rocket
import numpy as np

from ...agents.Agent import Agent
from ...utils.DataUtils import DataUtils
from ..DataElementException import DataElementException
from ..LearningElement import LearningElement
from ..DataElementConfig import DataElementConfig


@dataclass
class ROCKETExtractor(LearningElement):
    """
    ROCKET feature extractor.
    https://www.sktime.net/en/stable/api_reference/auto_generated/sktime.transformations.panel.rocket.Rocket.html
    """
    
    num_of_kernels : int = field(default=10000, metadata={"description": "Number of kernels used in the ROCKET model."})
    min_learning_samples : int = field(default=1, metadata={"description": "Number of Samples to learn on. Keep this, since ROCKET needs the sample only to instantiate the random kernels. Having more points does not improve performance."})
    min_inference_samples : int = field(default=1, metadata={"description": "Number of Samples to do inference on."})
    normalize : bool = field(default=True, metadata={"description": "Flag to indicate whether to normalize the input data using z-score normalization on the input batch."})
    
    def __post_init__(self):
        super().__post_init__()
        self.model = None
                
    def install(self, agent : Agent = None):
        super().install(agent)
        self.model = Rocket(num_kernels = self.num_of_kernels, n_jobs=-1, normalise=False, random_state=42) # We normalize the data in the LearningElement if required.
        
    
    def learn(self, data : dict, meta : dict = None) -> bool:
        """Learn the ROCKET model on the provided data."""
        if not self.model:
            raise DataElementException("Model is not installed. Call install() method first.")
        
        # Convert data
        dl = DataUtils.dict_to_ndarray(data)
        # # ROCKET accepts data of shape (n_instances, n_timepoints).Check if dl is 3D and first dimension is 1
        if dl.ndim == 3 and dl.shape[0] == 1:
            dl = dl.reshape(dl.shape[1], dl.shape[2]) # reshape to (n_instances, n_timepoints)
        self.model.fit(dl) 
        return False       
    
    def infer(self, data : dict, meta : dict = None) -> Tuple[Dict, Dict]:
        """Infer features using the ROCKET model."""
        if not self.model:
            raise ValueError("Model is not installed. Call install() method first.")
        
        forecast = {}
        for i, key in enumerate(data.keys()):
            d = np.array(data[key])
            transformed_data = self.model.transform(d).to_numpy().reshape(-1) # put everything into a flattened array
            transformed_data = np.nan_to_num(transformed_data, nan=0.0, posinf=0.0, neginf=0.0) # replace nan and inf with 0.0
            forecast[key + "-" + DataElementConfig.FEATURE + f"-ROCKET-{i}"] = transformed_data.tolist()  #convert to list
        
        return forecast, None



  
        
        
        
        # Convert transformed data back to a dictionary format
        return DataUtils.dataframe_to_dict(transformed_data), None