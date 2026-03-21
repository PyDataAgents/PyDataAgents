from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Union


from ..utils.SignalUtils import SignalUtils
from ..utils.MLUtils import MLUtils
from ..utils.DataUtils import DataUtils
from ..agents.AgentStates import AgentElementState, LearningState, NodeState
from .BufferNode import BufferNode

@dataclass
class LearningNode(BufferNode):
    """
    LearningNode is a base class for elements that require a learning step in their pipeline execution.
    It extends the BufferNode class and provides additional functionality specific to learning tasks.
    """

    min_learning_samples : int = field(default=0, metadata={"description": "Minimum number of samples required for learning."})
    min_inference_samples : int = field(default=0, metadata={"description": "Number of Samples to do inference on."})
    sample_length : int = field(default=0, metadata={"description": "Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed."})
    normalize : bool = field(default=False, metadata={"description": "Flag to indicate whether to normalize the input data using z-score normalization on the input batch."})
    nan_to_num : bool = field(default=False, metadata={"description": "If True, replace NaN/Inf values with finite numbers (0.0)."})

    def __post_init__(self):
        super().__post_init__()
        self._models : dict | Any = {} # Placeholder for the model, to be defined in subclasses.
        self._requires_learning : bool = True   # Flag indicating if learning is required. Can be overwritten in subclasses.
        self._state : Union[LearningState, NodeState, AgentElementState] = AgentElementState.UNINSTALLED
         
    @abstractmethod
    def learn(self, data : dict, meta : dict = None) -> bool:
        """ method that enables the training or continuous learning of the element.
        
        Returns:
            bool: if more learning is required the method returns True otherwise False
        """
            
    @abstractmethod
    def infer(self, data : dict, meta : dict = None) -> Tuple[Dict, Dict]:
        """ method that conducts the inference of the element's model/logic.
        """
    
    def detect_drift(self, data : dict, meta : dict = None) -> bool:
        """detects whether the model suffers from drift

        Returns:
            bool: true/false
        """
        return False
        
    def preprocess(self, data : dict):
        """Apply preprocessing transformations to the input data."""
        # Insert NanToNumTransform as second transformation if requested
        new_data : dict = data
        if self.nan_to_num:
            new_data = DataUtils.replace_nan(new_data)
        # Insert ReshapeTransform next if sample_length is specified (comes after nan cleaning per request)
        if self.sample_length > 0:
            # Determine insertion index: after potential nan_to_num (which would be at 1) or split key
            new_data = MLUtils.reshape(new_data, self.sample_length)
        # Normalize data if required (after reshape)
        if self.normalize:
            new_data = SignalUtils.zscore(new_data)

        return new_data
        
    def _on_execute(self):
        size = self.get_data_size()              
        if self._requires_learning and size >= max(1,self.sample_length)*self.min_learning_samples:
            self.n = max(1,self.sample_length)*self.min_learning_samples
            data = self.get_parent_data()
            meta = self.get_meta_info()            
            self._state = LearningState.PREPROCESSING     
            preprocessed_data = self.preprocess(data)
            # If we pass more than 1 value in the dictionary, we need to decide how to handle this. Either we train a model for each key or we concatenate all values.
            # We can do that here, or in the respective learn method of the subclass.
            # For now, we do that in the learning subclass and train a single model per key.
            self._state = LearningState.LEARNING
            self._requires_learning = self.learn(preprocessed_data, meta)        
        elif not self._requires_learning and size >= max(1,self.sample_length)*self.min_inference_samples:            
            self.n = max(1,self.sample_length)*self.min_inference_samples
            data = self.get_parent_data()
            meta = self.get_meta_info()        
            self._state = LearningState.PREPROCESSING         
            preprocessed_data = self.preprocess(data)
            self._state = LearningState.INFERING            
            model_data, meta = self.infer(preprocessed_data, meta)
            self.add_data(model_data)
            self.set_meta_info(meta)            
            if self.detect_drift(data, meta):
                self._requires_learning = True
                
    def requires_learning(self) -> bool:
        """Check if the node requires learning.

        Returns:
            bool: True if learning is required, False otherwise.
        """
        return self._requires_learning