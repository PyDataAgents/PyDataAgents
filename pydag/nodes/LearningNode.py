from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Union


from ..agents.AgentStates import AgentElementState, LearningState, NodeState
from .TransformNode import TransformNode
from .transforms.utils.ReshapeTransform import ReshapeTransform
from .transforms.statistics.ZScore import ZScore
from .transforms.utils.NanToNumTransform import NanToNumTransform


@dataclass
class LearningNode(TransformNode):
    """
    LearningNode is a base class for elements that require a learning step in their pipeline execution.
    It extends the TransformNode class and provides additional functionality specific to learning tasks.
    """

    min_learning_samples : int = field(default=0, metadata={"description": "Minimum number of samples required for learning."})
    min_inference_samples : int = field(default=0, metadata={"description": "Number of Samples to do inference on."})
    sample_length : int = field(default=0, metadata={"description": "Expected length of each sample. If 0, a sample with shape (1, min_learning_samples) is assumed. Otherwise, (1, sample_length) is assumed."})
    normalize : bool = field(default=False, metadata={"description": "Flag to indicate whether to normalize the input data using z-score normalization on the input batch."})
    nan_to_num : bool = field(default=False, metadata={"description": "If True, replace NaN/Inf values with finite numbers (0.0)."})

    def __post_init__(self):
        super().__post_init__()
        self._models : dict | Any = {} # Placeholder for the model, to be defined in subclasses.
        self._model_descriptors : dict | Any = {}
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
        if self.nan_to_num:
            self.transforms.insert(1, NanToNumTransform())
        # Insert ReshapeTransform next if sample_length is specified (comes after nan cleaning per request)
        if self.sample_length > 0:
            # Determine insertion index: after potential nan_to_num (which would be at 1) or split key
            insert_index = 2 if self.nan_to_num else 1
            self.transforms.insert(insert_index, ReshapeTransform(sample_length=self.sample_length))
        # Normalize data if required (after reshape)
        if self.normalize:
            # Place after reshape; compute index accordingly
            base_index = 3 if self.nan_to_num and self.sample_length > 0 else (
                2 if (self.nan_to_num or self.sample_length > 0) else 0
            )
            self.transforms.insert(base_index, ZScore())


        # Do other transformations
        if self.transforms is None or len(self.transforms) == 0:
            d = data
        
        else:
            d = data
            for transform in self.transforms:
                d = transform.transform(d)
        return d
        
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

    def snapshot_state(self) -> dict:
        payload = super().snapshot_state()
        payload["requires_learning"] = self._requires_learning
        payload["model_descriptors"] = self._serialize_models()
        return payload

    def restore_state(self, payload: dict | None):
        super().restore_state(payload)
        if payload is None:
            return
        self._requires_learning = payload.get("requires_learning", True)
        self._model_descriptors = payload.get("model_descriptors", {})

    def _serialize_models(self):
        if hasattr(self._models, "to_dict"):
            return self._models.to_dict()
        if isinstance(self._models, dict):
            descriptors = {}
            for key, value in self._models.items():
                if hasattr(value, "to_dict"):
                    descriptors[key] = value.to_dict()
                elif isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                    descriptors[key] = value
                else:
                    descriptors[key] = str(type(value).__name__)
            return descriptors
        if isinstance(self._models, (str, int, float, bool, list, dict)) or self._models is None:
            return self._models
        return str(type(self._models).__name__)
