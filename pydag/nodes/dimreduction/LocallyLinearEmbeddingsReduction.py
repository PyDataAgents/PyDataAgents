from dataclasses import dataclass, field
from typing import Dict, Tuple
from sklearn.manifold import LocallyLinearEmbedding
import numpy as np

from ...agents.Agent import Agent
from ..LearningElement import LearningElement
from ..DataElementConfig import DataElementConfig

@dataclass
class LocallyLinearEmbeddingsReduction(LearningElement):
    """Dimensionality reduction using LocallyLinearEmbeddings algorithm. Mind, that the Algorithms is trained on two dimensional data with shape (n_samples, n_features). 
    Hence sample_length should be larger than the number of dimensions. 

    """
    
    dimensions : int = field(default=2, metadata={"decsription": "number of dimensions to reduce the data to"})
    
    def __post_init__(self):
        super().__post_init__()
        self.models = {}    
    
    def install(self, agent : Agent = None):
        super().install(agent)
        
    def learn(self, data : dict, meta : dict = None) -> bool:
        for i, key in enumerate(data.keys()):
            self.models[key] = LocallyLinearEmbedding(n_components=self.dimensions) # Add a new model
            d = np.array(data[key])
            if d.ndim == 1:
                d = d.reshape(1, -1)  # Reshape to 2D array with one sample
            elif d.ndim == 3:
                d = np.squeeze(d, axis=0) 
            self.models[key].fit(d)
        return False
            
    def infer(self, data : dict, meta : dict = None) -> Tuple[Dict, Dict]:
        forecast = {}
        for i, key in enumerate(data.keys()):
            d = np.array(data[key])
            if d.ndim == 1:
                d = d.reshape(1, -1)  # Reshape to 2D array with one sample
            elif d.ndim == 3:
                d = np.squeeze(d, axis=0) 
            transformed_data = self.models[key].transform(d).reshape(-1) # put everything into a flattened array
            forecast[key + "-" + DataElementConfig.FEATURE + f"-LLE"] = transformed_data.tolist()  #convert to list
        
        return forecast, None