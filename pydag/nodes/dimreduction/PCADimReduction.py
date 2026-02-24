from dataclasses import dataclass, field
from typing import Dict, Tuple
from sklearn.decomposition import KernelPCA
import numpy as np


from ..LearningNode import LearningNode
from ...agents.AgentConfig import AgentConfig

@dataclass
class PCADimReduction(LearningNode):
    """Dimensionality reduction using PCA algorithm. Mind, that the Algorithms is trained on two dimensional data with shape (n_samples, n_features). 
    Hence sample_length should be larger than the number of dimensions. 

    """
    
    dimensions : int = field(default=2, metadata={"decsription": "number of dimensions to reduce the data to"})
    output_keys : list[str] = field(default_factory=list, metadata={"description": "optional explicit output keys; if empty, default naming is used"})
                
    def learn(self, data : dict, meta : dict = None) -> bool:
        for i, key in enumerate(data.keys()):
            self._models[key] = KernelPCA(n_components=self.dimensions, kernel="rbf") # Add a new model
            d = np.array(data[key])
            if d.ndim == 1:
                d = d.reshape(1, -1)  # Reshape to 2D array with one sample
            elif d.ndim == 3:
                d = np.squeeze(d, axis=0) 
            self._models[key].fit(d)
        return False
            
    def infer(self, data : dict, meta : dict = None) -> Tuple[Dict, Dict]:
        forecast = {}
        for i, key in enumerate(data.keys()):
            d = np.array(data[key])
            if d.ndim == 1:
                d = d.reshape(1, -1)  # Reshape to 2D array with one sample
            elif d.ndim == 3:
                d = np.squeeze(d, axis=0) 
            transformed_data = self._models[key].transform(d).reshape(-1) # put everything into a flattened array
            if len(data.keys()) == len(self.output_keys):
                forecast[self.output_keys[i]] = transformed_data.tolist()  #convert to list
            else:
                forecast[self.cname() + "-" + AgentConfig.FEATURE + "-" + f"{i}"] = transformed_data.tolist()  #convert to list
        
        return forecast, None
        
        
