from dataclasses import dataclass, field
import enum
import string
from typing import Dict, Tuple
import numpy as np
from scipy.spatial import KDTree
from scipy.spatial.distance import jensenshannon
from scipy.stats import wasserstein_distance

from ...agents.AgentKeywords import AgentKeywords
from ..LearningNode import LearningNode


class CompareMode(str, enum.Enum):
    RLG = "RLG" # default
    JSD = "JSD" # Jensen-Shannon Divergence: The "per-bin-Version" of the Jensen-Shannon Divergence is used to detect outliers in the data.
    EMD = "EMD" # Earth Mover's Distance: The "per-bin-Version" of the Earth Mover's Distance is used to detect outliers in the data.
    JSD_GLOBAL = "JSD-Global" # Jensen-Shannon Divergence global: The Jensen-Shannon Divergence is used to detect outliers in the data. The original JSD distance is calculated on A and A' where A' is A+x_n and x_n is the point at step n.
    EMD_GLOBAL = "EMD-Global" # Earth Mover's Distance global: The Earth Mover's Distance is used to detect outliers in the data. The original EMD distance is calculated on A and A' where A' is A+x_n and x_n is the point at step n.

@dataclass
class ShiftMonitoring(LearningNode):

    """
    ShiftMonitoring is a LearningNode that monitors distributional shifts in incoming data. It uses statistical methods to compare the distribution of new data against learned distributions and can identify when a significant shift occurs.
    Returns the deviation as well as the outlier-decision to the first distribution "A", even if n_distributions > 2.
    """

    
    inference_buffer_size : int = field(default=10e6, metadata={"description": "Size of the buffer for the inference data. This is the data which is appended to the training data to calculate the distribution to compare with the distribution of the training data."})
    bin_count : int = field(default=10, metadata={"description": "number of bins per dimension of the grid. Each dimension is spanned by one value of the input data, e.g. if you have data like [[10,2,2],....,[12,2,5]], the first dimension is spanned by the values [10, ..., 12 ] and so on. Can be imagined as the # of squares in x and y direction. The features are binned to the number of bins to calculate the distribution."})
    compare_mode : str = field(default=CompareMode.JSD.value, metadata={"description": "The comparison function which is used to compare the distribution of the training data with the distribution of the inference data."})
    n_distributions : int = field(default=2, metadata={"description" : "The number of distributions which can be calculated from the data. If set to 2, all points which deviate from A are put to A'. This is similar to distribution shift monitoring from an initial base distribution, like e.g. an Process in OK-State or the like. If set to n, points which deviate from A .... A^(n-1) are put to A^n. n > 2 is not implemented yet."})
    return_input : bool = field(default=False, metadata={"description": "if True the input data is returned in the output dictionary as well"})
    sensitivity : float = field(default=1.0, metadata={"description": "Sensitivity factor for threshold calculation in units of standard deviations. Higher values make the detection less sensitive."})
    shift_name : str = field(default="shift", metadata={"description": "The name of the shift feature in the output dictionary."})
    decision_name : str = field(default="decision", metadata={"description": "The name of the decision feature in the output dictionary."})

    def __post_init__(self):
        self._models = {}
        super().__post_init__()
        
    def preprocess(self, data: dict):
        d = super().preprocess(data)
        # Check if values dimension of d is longer than 4. If so, we need to reduce the dimensionality first since this leads to problems in the histogram calculation since the resulting histogram has size bin_count^dimensions which can lead to memory issues.
        if np.array(list(d.values())[0]).shape[-1] > 4: # We assume that all values have the same shape.
            raise ValueError(f"Input data has too many dimensions ({np.array(list(d.values())[0]).shape[-1]}). Please reduce the dimensionality to 4 or less before using ShiftMonitoring. The resulting histogram has size {self.bin_count**np.array(list(d.values())[0]).shape[-1]} which can lead to memory issues.")
        return d

    def learn(self, data : dict, meta : dict = None) -> bool:
        
        for i, key in enumerate(data.keys()):
            self._models[key] = DistributionMonitoring(self.inference_buffer_size, self.bin_count, self.compare_mode, self.n_distributions, self.return_input, key, self.sensitivity) # Add a new model
            d = np.array(data[key])
            if d.ndim == 1:
                d = d.reshape(1, -1)  # Reshape to 2D array with one sample
            elif d.ndim == 3:
                d = np.squeeze(d, axis=0) 
            self._models[key].fit(d)
        return False   
    
    
    def infer(self, data : dict, meta: dict) -> Tuple[Dict, Dict]:
        forecast = {}
        for i, key in enumerate(data.keys()):
            d = np.array(data[key])
            if d.ndim == 1:
                d = d.reshape(1, -1)  # Reshape to 2D array with one sample
            elif d.ndim == 3:
                d = np.squeeze(d, axis=0) 
            transformed_data, decision = self._models[key].transform(d)
            forecast[f"{key}-{AgentKeywords.FEATURE}-{self.shift_name}"] = transformed_data[0].tolist()  #convert to list
            forecast[f"{key}-{AgentKeywords.FEATURE}-{self.decision_name}"] = decision.tolist()  #convert to list
            if self.return_input:
                for index in d:
                    for f,feat in enumerate(index):
                        forecast[key+f"-{f}"] = feat.tolist()
        
        return forecast, None
        
class DistributionA():
        
    def __init__(self, A, initialization_edges=None, initialization_KDTree=None,  compare_mode = None, bin_count = None, bins= None):
        # We want to have one variable per feature where the bins are calculated based on the values. We want to calculate the realtive number per bin.
        self.x = self.check_data_dimensionality(A)
        self.compare_mode = compare_mode
        self.bin_count = bin_count
        self.bins = bins
        self.initialization_edges = initialization_edges
        self.initialization_KDTree = initialization_KDTree
        
        
        # Compute the bin edges for the histogram
        self.num_dims = self.x.shape[1]  # Number of dimensions
        self.bin_edges = []

        for dim in range(self.num_dims):
            min_val = np.min(self.x[:, dim])
            max_val = np.max(self.x[:, dim])
            mean = np.mean(self.x[:, dim])
            std = np.std(self.x[:, dim])

            # Define the lower and upper extended limits
            lower_bound = min_val - 3 * std
            upper_bound = max_val + 3 * std

            # Create bins:
            # First bin: [lower_bound, min_val]
            # Middle bins: linspace between min_val and max_val
            # Last bin: [max_val, upper_bound]
            middle_bins = np.linspace(min_val, max_val, self.bin_count - 1)  # Exclude first and last bins
            edges = np.concatenate(([lower_bound], middle_bins, [upper_bound]))

            if std == 0:
                self.bin_edges = self.bin_edges.append(self.initialization_edges)
            else:
                self.bin_edges.append(edges)                      

        match self.compare_mode:
            case CompareMode.RLG.value:
                self.hist, self.edges = np.histogramdd(self.x, bins=self.bin_edges, density=False)
                # Calculate the standard deviation for all histogram dimensions, only considering non-empty bins
                self.non_empty_bins_coordinates = list(zip(*np.nonzero(self.hist)))
                self.empty_bins_coordinates = list(zip(*np.where(self.hist == 0))) # Distances of all empty bins to the
                self.flattened_hist = self.hist.flatten()/np.sum(self.hist)
                self.non_empty_bins = self.flattened_hist != 0
                self.non_empty_bins_indices = np.where(self.non_empty_bins)
                
                self.empty_bin_indices = np.where(~self.non_empty_bins)
                self.flattened_hist_nonempty = self.flattened_hist[self.non_empty_bins]
                self.std_flattened_hist  = np.nan_to_num(np.std(self.flattened_hist_nonempty))
                self.mean_flattened_hist = np.nan_to_num(np.mean(self.flattened_hist_nonempty))


                # Compute mean distance between all non empty bins
                self.bin_tree = KDTree(self.non_empty_bins_coordinates)
                self.mean_dist_occupied_bins = np.mean(self.bin_tree.query(self.non_empty_bins_coordinates, k=2)[0][:, 1]) # finds the two closest bins for each occupied bin. k=2 because the first nearest neighbor is the bin itself (distance = 0). The second closest bin is the actual nearest other occupied bin. [0] extracts the distances (not indices).
                if np.isfinite(self.mean_dist_occupied_bins) == False:
                    self.bin_tree = self.initialization_KDTree
                    self.mean_dist_occupied_bins = np.mean(self.bin_tree.query(self.non_empty_bins_coordinates, k=2)[0][:, 1])
            
            case CompareMode.JSD.value:
                self.hist, self.edges = np.histogramdd(self.x, bins=self.bin_edges, density=False)
                # Calculate the standard deviation for all histogram dimensions, only considering non-empty bins
                self.non_empty_bins_coordinates = list(zip(*np.nonzero(self.hist)))
                self.empty_bins_coordinates = list(zip(*np.where(self.hist == 0))) # Distances of all empty bins to the
                self.flattened_hist = self.hist.flatten()/np.sum(self.hist)
                self.non_empty_bins = self.flattened_hist != 0
                self.non_empty_bins_indices = np.where(self.non_empty_bins)
                
                self.empty_bin_indices = np.where(~self.non_empty_bins)
                self.flattened_hist_nonempty = self.flattened_hist[self.non_empty_bins]
                self.std_flattened_hist  = np.nan_to_num(np.std(self.flattened_hist_nonempty))
                self.mean_flattened_hist = np.nan_to_num(np.mean(self.flattened_hist_nonempty))

                # Compute mean distance between all non empty bins
                self.bin_tree = KDTree(self.non_empty_bins_coordinates)
                self.mean_dist_occupied_bins = np.mean(self.bin_tree.query(self.non_empty_bins_coordinates, k=2)[0][:, 1]) # finds the two closest bins for each occupied bin. k=2 because the first nearest neighbor is the bin itself (distance = 0). The second closest bin is the actual nearest other occupied bin. [0] extracts the distances (not indices).
                if np.isfinite(self.mean_dist_occupied_bins) == False:
                    self.bin_tree = self.initialization_KDTree
                    self.mean_dist_occupied_bins = np.mean(self.bin_tree.query(self.non_empty_bins_coordinates, k=2)[0][:, 1])
             
            case CompareMode.JSD_GLOBAL.value:
                self.hist, self.edges = np.histogramdd(self.x, bins=self.bin_edges, density=False)
                # Calculate the standard deviation for all histogram dimensions, only considering non-empty bins
                self.non_empty_bins_coordinates = list(zip(*np.nonzero(self.hist)))
                self.empty_bins_coordinates = list(zip(*np.where(self.hist == 0))) # Distances of all empty bins to the
                self.flattened_hist = self.hist.flatten()/np.sum(self.hist)
                self.non_empty_bins = self.flattened_hist != 0
                self.non_empty_bins_indices = np.where(self.non_empty_bins)
                
                self.empty_bin_indices = np.where(~self.non_empty_bins)
                self.flattened_hist_nonempty = self.flattened_hist[self.non_empty_bins]
                self.std_flattened_hist  = np.nan_to_num(np.std(self.flattened_hist_nonempty))
                self.mean_flattened_hist = np.nan_to_num(np.mean(self.flattened_hist_nonempty))

                # Compute mean distance between all non empty bins
                self.bin_tree = KDTree(self.non_empty_bins_coordinates)
                self.mean_dist_occupied_bins = np.mean(self.bin_tree.query(self.non_empty_bins_coordinates, k=2)[0][:, 1]) # finds the two closest bins for each occupied bin. k=2 because the first nearest neighbor is the bin itself (distance = 0). The second closest bin is the actual nearest other occupied bin. [0] extracts the distances (not indices).
                if np.isfinite(self.mean_dist_occupied_bins) == False:
                    self.bin_tree = self.initialization_KDTree
                    self.mean_dist_occupied_bins = np.mean(self.bin_tree.query(self.non_empty_bins_coordinates, k=2)[0][:, 1])
             
            case CompareMode.EMD_GLOBAL.value:
                self.hist, self.edges = np.histogramdd(self.x, bins=self.bin_edges, density=False)
                # Calculate the standard deviation for all histogram dimensions, only considering non-empty bins
                self.non_empty_bins_coordinates = list(zip(*np.nonzero(self.hist)))
                self.empty_bins_coordinates = list(zip(*np.where(self.hist == 0))) # Distances of all empty bins to the
                self.flattened_hist = self.hist.flatten()/np.sum(self.hist)
                self.non_empty_bins = self.flattened_hist != 0
                self.non_empty_bins_indices = np.where(self.non_empty_bins)
                
                self.empty_bin_indices = np.where(~self.non_empty_bins)
                self.flattened_hist_nonempty = self.flattened_hist[self.non_empty_bins]
                self.std_flattened_hist  = np.nan_to_num(np.std(self.flattened_hist_nonempty))
                self.mean_flattened_hist = np.nan_to_num(np.mean(self.flattened_hist_nonempty))

                # Compute mean distance between all non empty bins
                self.bin_tree = KDTree(self.non_empty_bins_coordinates)
                self.mean_dist_occupied_bins = np.mean(self.bin_tree.query(self.non_empty_bins_coordinates, k=2)[0][:, 1]) # finds the two closest bins for each occupied bin. k=2 because the first nearest neighbor is the bin itself (distance = 0). The second closest bin is the actual nearest other occupied bin. [0] extracts the distances (not indices).
                if np.isfinite(self.mean_dist_occupied_bins) == False:
                    self.bin_tree = self.initialization_KDTree
                    self.mean_dist_occupied_bins = np.mean(self.bin_tree.query(self.non_empty_bins_coordinates, k=2)[0][:, 1])
              
            case CompareMode.EMD.value:
                self.hist, self.edges = np.histogramdd(self.x, bins=self.bin_edges, density=False)
                # Calculate the standard deviation for all histogram dimensions, only considering non-empty bins
                self.non_empty_bins_coordinates = list(zip(*np.nonzero(self.hist)))
                self.empty_bins_coordinates = list(zip(*np.where(self.hist == 0))) # Distances of all empty bins to the
                self.flattened_hist = self.hist.flatten()/np.sum(self.hist)
                self.non_empty_bins = self.flattened_hist != 0
                self.non_empty_bins_indices = np.where(self.non_empty_bins)
                
                self.empty_bin_indices = np.where(~self.non_empty_bins)
                self.flattened_hist_nonempty = self.flattened_hist[self.non_empty_bins]
                self.std_flattened_hist  = np.nan_to_num(np.std(self.flattened_hist_nonempty))
                self.mean_flattened_hist = np.nan_to_num(np.mean(self.flattened_hist_nonempty))

                # Compute mean distance between all non empty bins
                self.bin_tree = KDTree(self.non_empty_bins_coordinates)
                self.mean_dist_occupied_bins = np.mean(self.bin_tree.query(self.non_empty_bins_coordinates, k=2)[0][:, 1]) # finds the two closest bins for each occupied bin. k=2 because the first nearest neighbor is the bin itself (distance = 0). The second closest bin is the actual nearest other occupied bin. [0] extracts the distances (not indices).
                if np.isfinite(self.mean_dist_occupied_bins) == False:
                    self.bin_tree = self.initialization_KDTree
                    self.mean_dist_occupied_bins = np.mean(self.bin_tree.query(self.non_empty_bins_coordinates, k=2)[0][:, 1])
    
    @classmethod
    def check_data_dimensionality(self, x):
        # x can come as arra or dict but should be a numpy array.
        if isinstance(x, dict):
            # Convert the dictionary to a numpy array
            x = x.x      
        
        # Reduce the `values` dimension (e.g., by taking the mean) - currently this is not effective since the feature dimension is 1 by default.
        if np.ndim(x) == 3:
            aggregated_data = np.mean(x, axis=1)  # Shape: (samples, features)
            return aggregated_data
        elif np.ndim(x) == 2:
            aggregated_data = x  # Shape: (samples, features)
            return aggregated_data
        else:
            raise ValueError("Input data must be 2D or 3D. Please check the input data shape.")
        
class DistributionAPrime(DistributionA):
        
    def __init__(self, A, x, compare_mode = None, bin_count = None, bins= None):
        self.distance_function_parameters = {}
        self.distribution_parameters = {}
        self.A = A
        self.compare_mode = compare_mode
        self.bin_count = bin_count
        self.bins = bins
        self.x = self.add_inference_data(self.A, x)  # Shape: (samples, features)       

        self.hist_inference, self.edges_inference = np.histogramdd(self.x, bins=self.A.bin_edges, density=False)
        self.non_empty_bins_inference_coordinates = list(zip(*np.nonzero(self.hist_inference)))
        
        # Get multi-dimensional bin indices
        self.bin_indices = [np.digitize(self.x[:, i], self.A.bin_edges[i]) - 1 for i in range(self.x.shape[1])]      
        self.bin_indices = np.array(self.bin_indices).T  # Shape: (num_samples, num_dims)
        
        # Clip indices to stay within valid range
        self.bin_indices = np.clip(self.bin_indices, 0, np.array([len(edge) - 2 for edge in self.A.edges]))
       
        # calculate the distance to the nearest occupied bin. Helps to find outliers which are far away from the other bins.
        self.distance_to_nearest_occupied_bins = np.nan_to_num(np.mean(self.A.bin_tree.query(self.A.empty_bins_coordinates, k=2)[0]/self.A.mean_dist_occupied_bins, axis=1), posinf=0, neginf=0) if self.A.mean_dist_occupied_bins >0 else np.zeros_like(np.mean(self.A.bin_tree.query(self.A.empty_bins_coordinates, k=2)[0], axis=1))  # We want to get the mean distance of all empty bins to the two neares filled bins. If, during inference a datapoint falls into anformerly empty bin, it gets a higher weight.

        # convert the bin indices to a single index
        # Compute the multiplier for each dimension
        self.multipliers = np.cumprod([1] + list(np.shape(self.A.hist)[:-1]))[::-1] # The data has the shape (num_samples, num_dims). Though, we need a last dimension whichis the values dimension per sample which is always one in our case.
        # Compute flattened bin indices for N-dimensional case
        self.flattened_bin_indices = np.sum(self.bin_indices * self.multipliers, axis=1)
    
        match self.compare_mode:
            case CompareMode.JSD_GLOBAL.value:
                self.flattened_hist_inference = self.hist_inference.flatten()/np.sum(self.hist_inference) if np.sum(self.hist_inference) > 0 else self.hist_inference.flatten()
                
            case CompareMode.JSD.value:
                # JSD with additional distance information
                self.flattened_hist_inference = self.hist_inference.flatten()/np.sum(self.hist_inference) if np.sum(self.hist_inference) > 0 else self.hist_inference.flatten()
                # Jenson Shannon Divergence per bin
                self.A.flattened_hist += 1e-10
                self.flattened_hist_inference += 1e-10
                self.flattened_mean_hist = 0.5*(self.A.flattened_hist + self.flattened_hist_inference)
                # Get row and column indices
                #rows, cols = np.indices(self.hist_inference.shape)
                # Combine the indices into a list of (row, col) pairs
                indices = np.stack(np.indices(self.hist_inference.shape), axis=-1)
                self.distance_to_nearest_occupied_bin = np.mean(self.A.bin_tree.query([tuple(i) for i in list(indices.reshape(-1,self.A.num_dims))], k=2)[0]/self.A.mean_dist_occupied_bins, axis=1)

            case CompareMode.EMD_GLOBAL:
                self.flattened_hist_inference = self.hist_inference.flatten()/np.sum(self.hist_inference) if np.sum(self.hist_inference) > 0 else self.hist_inference.flatten()

            case CompareMode.EMD.value:
                self.flattened_hist_inference = self.hist_inference.flatten()/np.sum(self.hist_inference) if np.sum(self.hist_inference) > 0 else self.hist_inference.flatten()
                non_empty_bins = self.flattened_hist_inference > 0
                self.non_empty_bins_indices_inference = np.where(non_empty_bins)
                self.flattened_hist_inference_nonempty = self.flattened_hist_inference[non_empty_bins]
                self.std_flattened_hist_inference = np.nan_to_num(np.std(self.flattened_hist_inference_nonempty)) # Comparison between std_flattened_hist_inference and std_flattened_hist allows to make an assumpation about the change in the distribution. A higher standard deviation lets us reason about more extreme values.

            case CompareMode.RLG.value:            
                # Calculate the standard deviation for all histogram dimensions, only considering non-empty bins
                self.flattened_hist_inference = self.hist_inference.flatten()/np.sum(self.hist_inference) if np.sum(self.hist_inference) > 0 else self.hist_inference.flatten()
                self.non_empty_bins = self.flattened_hist_inference > 0
                self.non_empty_bins_indices_inference = np.where(self.non_empty_bins)
                self.flattened_hist_inference_nonempty = self.flattened_hist_inference[self.non_empty_bins]
                self.std_flattened_hist_inference = np.nan_to_num(np.std(self.flattened_hist_inference_nonempty)) if len(self.flattened_hist_inference_nonempty) > 0 else 1 # Comparison between std_flattened_hist_inference and std_flattened_hist allows to make an assumpation about the change in the distribution. A higher standard deviation lets us reason about more extreme values.
                # Localitez Jenson Shannon Divergence
                delta = 1e-10 # Prevent division by zero.
                self.flattened_mean_hist = 0.5*(self.A.flattened_hist + self.flattened_hist_inference + delta)
                self.JSD = 0.5*((self.A.flattened_hist+delta)*np.log((self.A.flattened_hist + delta) /self.flattened_mean_hist)+(self.flattened_hist_inference+delta)*np.log((self.flattened_hist_inference+delta)/self.flattened_mean_hist))
                
                # Ensure that the values in the denominator are != 0.
                self.r_1 = -np.log10(self.A.std_flattened_hist) if self.A.std_flattened_hist > 0 else 1
                self.r_2 = self.A.mean_flattened_hist if self.A.mean_flattened_hist > 0 else 1
                self.r_3 = self.distance_to_nearest_occupied_bins

    @classmethod
    def add_inference_data(self, A, x):
        # Add a point to a distribution
        x = self.check_data_dimensionality(x)
        A_prime = A.x.copy()  # Create a copy of the distribution to avoid modifying the original one    
        A_prime = np.append(A_prime, x, axis=0)    
        return A_prime
    

class DistributionMonitoring():
    def __init__(self, inference_buffer_size, bin_count, compare_mode, n_distributions, return_input, key, sensitivity):
        self.conclusions = {}
        self.prediction = {}
        self.statistical_values = {}
        self.threshold_counter = 0
        self.x_inference = None 
        self.A = {}
        self.A_prime = {}
        self.counter = 0
        self.distributions = None
        self.key_colors = None 
        self.difference_scores = {}
        self.concl = {}
        self.bins = None


        self.inference_buffer_size = inference_buffer_size
        self.bin_count = bin_count
        self.compare_mode = compare_mode
        self.n_distributions = n_distributions
        self.return_input = return_input
        self.key = key
        self.sensitivity = sensitivity


        self.distributions, self.key_colors = self.setup_distributions(self.n_distributions)
        self.distributions_to_int = {key: i for i, key in enumerate(self.distributions.keys())} # Distribution "A" gets the value 0, "B" gets the value 1 and so on.


    def fit(self, x):
        self.counter += 1
        # We need initialization edges for cases with only one or two datapoints.
        # We assume that the first distribution is the base distribution with the most data points.
        if self.distributions["A"] is not None:
            self.initialization_edges = self.distributions["A"].bin_edges
        else:
            self.initialization_edges = None

        # We need an initialization bin-tree for cases, where all points fall into one bin (this is often the case with very few points - like one point at the beginning).
        if self.distributions["A"] is not None:
            self.initialization_KDTree = self.distributions["A"].bin_tree
        else:
            self.initialization_KDTree = None

        for key in self.distributions.keys():
            if self.distributions[key] is None:
                self.distributions[key] = DistributionA(x, initialization_edges = self.initialization_edges, initialization_KDTree = self.initialization_KDTree, compare_mode = self.compare_mode, bin_count = self.bin_count, bins = self.bins)
                self.set_threshold(self.distributions[key])                
                return key

    def transform(self, x):
        if self.x_inference is None:
            self.x_inference = np.append(self.distributions["A"].x, x, axis=0)
        else:
            self.x_inference = np.append(self.x_inference, x, axis=0)
        self.concl = {}
        self.difference_scores = {}
        self.distributions["B"] = DistributionAPrime(self.distributions["A"], self.x_inference, compare_mode = self.compare_mode, bin_count = self.bin_count, bins = self.bins)
        self.difference_scores["A"] = self.calculate_distance(self.distributions["A"], self.distributions["B"])
        if self.distributions["A"].threshold_counter >= self.distributions["A"].threshold_setter:
            self.concl["A"] = sum(self.set_conclusion_method(self.difference_scores["A"], self.distributions["A"]))
            print(f"A | {self.difference_scores['A']} | {self.distributions['A'].threshold} | {self.concl['A']}")

        self.counter += 1
   
        return self.difference_scores["A"], self.concl["A"] # Always return the closest distribution if a point was assigned.
    
    
    """
    def transform(self, x):
        self.concl = {}
        distr_count = 0
        self.difference_scores = {}
        self.inference_distributions = {}
        for key in self.distributions.keys():
            if self.distributions[key] is not None:
                distr_count += 1
                self.inference_distributions[key] = DistributionAPrime(self.distributions[key], x, compare_mode= self.compare_mode, bin_count = self.bin_count, bins = self.bins)
                self.difference_scores[key] = self.calculate_distance(self.distributions[key], self.inference_distributions[key])
                if self.distributions[key].threshold_counter >= self.distributions[key].threshold_setter:
                    self.concl[key]=sum(self.set_conclusion_method(self.difference_scores[key], self.distributions[key]))
                    print(f"{key} | {self.difference_scores[key]} | {self.distributions[key].threshold} | {self.concl[key]}")
        if self.counter % 10 == 0:
            self.plot()
   
        # Check if the difference scores are above the threshold for all distributions --> Then assign the point to a new distribution.
        if all([a > 0 for a in self.concl.values()]):
            # Assign the point to a new distribution if not already all distributions are filled.
            if len(self.concl.keys()) < self.n_distributions:
                best_distribution = self.fit(x)
            else:
                #best_distribution = self.assign_to_distribution(x)
                best_distribution = None # If it is not part of an existing distribution, it should not be assigned to any distribution.
        elif any([a >= 0 for a in self.concl.values()]):
            # Only if a point is very close to a distribution, assign it. Otherwise, if assignment is forced even if all points are below the threshold but the point is not close to any, this motivates the assignment to a wrong distribution.
            # This is done in the assign_to_distribution method.
            best_distribution = self.assign_to_distribution(x)
        else:
            best_distribution = None
            pass
        self.counter += 1     
        print(f"Assigned to distribution {best_distribution}")

        return self.difference_scores["A"], best_distribution # Always return the closest distribution if a point was assigned."""
    


    
    
    """
    def assign_to_distribution(self, x):
        # assign the point to the distribution with the lowest difference score.
        #self.difference_scores = {key:abs((self.difference_scores[key]["features"]*len(self.distributions[key].x))-self.distributions[key].threshold)/self.distributions[key].threshold for key in [k for k,v in self.concl.items() if v ==0]}
        self._difference_scores = {key:abs((self.difference_scores[key]*len(self.distributions[key].x))-self.distributions[key].threshold)/self.distributions[key].threshold for key in self.concl.keys()}
        min_score = min([k for k in self._difference_scores.values()])
        best_distribution = [key for key, value in self._difference_scores.items() if value == min_score][0]
        # Only if a point is very close to a distribution, assign it. Otherwise, if assignment is forced even if all points are below the threshold but the point is not close to any, this motivates the assignment to a wrong distribution.
        # Only if min_score is significantly lower as compared to the other _difference_scores, we assign it to the corresponding distribution. If all scores are very similar, we do not assign it to any distribution.
        # Consider all distributions except the best_distribution
        other_scores = [v for k, v in self._difference_scores.items() if k != best_distribution]
        if other_scores:
            mean_others = np.mean(other_scores)
            std_others = np.std(other_scores)
        else:
            mean_others = 0
            std_others = 0

        if min_score < mean_others - 1.5 * std_others:
            self.distributions[best_distribution].x = DistributionAPrime.add_inference_data(self.distributions[best_distribution], x) 
            self.distributions[best_distribution] = DistributionA(self.distributions[best_distribution].x, compare_mode = self.compare_mode, bin_count = self.bin_count, bins = self.bins)
            self.set_threshold(self.distributions[best_distribution])
            return best_distribution"""


    def calculate_distance(self, A, A_prime):
        self.params = {}

        self.A = A
        self.A_prime = A_prime

        match self.compare_mode:
            case CompareMode.JSD_GLOBAL.value:
                self.diff = np.ones_like(self.A_prime.flattened_hist_inference)
                self.diff = self.diff*jensenshannon(self.A_prime.flattened_hist_inference, self.A.flattened_hist, base=np.e) # Jenson-Shannon Divergence per bin. The base is 2 to get the result in bits.
      
            case CompareMode.JSD.value:
                self.diff = np.zeros_like(self.A_prime.flattened_hist_inference)
                self.diff = self.A_prime.distance_to_nearest_occupied_bin*0.5*(self.A.flattened_hist*np.log(self.A.flattened_hist/self.A_prime.flattened_mean_hist)+self.A_prime.flattened_hist_inference*np.log(self.A_prime.flattened_hist_inference/self.A_prime.flattened_mean_hist))
            
            case CompareMode.EMD_GLOBAL.value:
                self.diff = np.ones_like(self.A_prime.flattened_hist_inference)
                self.diff = self.diff*wasserstein_distance(self.A_prime.flattened_hist_inference, self.A.flattened_hist) # Jenson-Shannon Divergence per bin. The base is 2 to get the result in bits.
            
            case CompareMode.EMD.value:
                self.diff = np.zeros_like(self.A_prime.flattened_hist_inference)
                # Earth Movers distance
                self.A.flattened_hist += 1e-10
                self.A_prime.flattened_hist_inference += 1e-10
                for bin_inference_indice in self.A_prime.non_empty_bins_inference_coordinates:
                    for bin_base_indice in self.A.non_empty_bins_coordinates:
                        # Calculate the distance between the two bins
                        dist = np.linalg.norm(np.array(bin_inference_indice) - np.array(bin_base_indice))
                        # Calculate the contribution to the EMD
                        bin_inference_indice_flat = np.sum(bin_inference_indice * self.A_prime.multipliers)
                        bin_base_indice_flat = np.sum(bin_base_indice * self.A_prime.multipliers)
            
                        self.diff[bin_inference_indice_flat] += np.abs((self.A.flattened_hist[bin_base_indice_flat] - self.A_prime.flattened_hist_inference[bin_inference_indice_flat])) * dist
        
            case CompareMode.RLG.value:
                non_empty_bins = self.A.non_empty_bins
                self.diff = np.zeros_like(self.A_prime.flattened_hist_inference)
                self.diff[non_empty_bins] = np.nan_to_num((1/self.A_prime.r_1)*np.abs(1-(self.A_prime.flattened_hist_inference[non_empty_bins]/self.A.flattened_hist[non_empty_bins])))
                self.diff[~non_empty_bins] = np.nan_to_num((self.A_prime.r_3/self.A_prime.r_1)*np.abs((self.A_prime.flattened_hist_inference[~non_empty_bins]-self.A_prime.r_2)/(self.A_prime.r_2)))
                self.diff *= self.A_prime.JSD            

        self.set_prediction(self.A_prime)
        return self.prediction
    
    def set_conclusion_method(self, data, distribution):
        concl = np.where(data>= distribution.threshold, 1, 0)
        return concl

    def set_prediction(self, A_prime):
        # Assign the anomaly score to each sample
        A_prime.bin_indices_to_diff = np.zeros_like(A_prime.flattened_bin_indices.astype(float))
        A_prime.bin_indices_to_diff[:] = self.diff[A_prime.flattened_bin_indices]
        self.prediction = A_prime.bin_indices_to_diff[-1].reshape(1, -1) # convert to a 1D Numpy Array with shape (values,features)
        
    
    def set_threshold(self, A):        
        A.threshold_counter = 0
        A.threshold_scores = []
        A.threshold_setter = len(A.x)
        for x in A.x:
            # Since each x from A.x is used, x is existing twice in the data. We slightly augment each element (dimension) in x to prevent that it is exactly the same. 
            x_noise = np.array([x_ + np.random.normal(0, abs(x_)*0.05) for x_ in x]).copy()
            if np.ndim(x_noise) == 1:
                x_noise = np.expand_dims(x_noise, axis=0)
                x_noise = np.expand_dims(x_noise, axis=1) # x has two dimensions - must have shape n,1,m.
            elif np.ndim(x_noise) == 2:
                x_noise = np.expand_dims(x_noise, axis=1)
            else:
                pass
            A_ = DistributionAPrime(A, x_noise, compare_mode= self.compare_mode, bin_count = self.bin_count, bins = self.bins)
            score = self.calculate_distance(A, A_)[0] 

            A.threshold_scores.append(score)
            A.threshold = np.mean(A.threshold_scores) + self.sensitivity* np.std(A.threshold_scores)
            A.threshold_counter += 1
        thresholds_ = [] # In case the threshold is 0 or very low, we set it to the threshol of the base distribution.
        for key in self.distributions.keys():
            if self.distributions[key] is not None:
                thresholds_.append(self.distributions[key].threshold) 
        mean_thresholds_ = np.mean(thresholds_)
        std_thresholds_ = np.std(thresholds_)
        if A.threshold < max(mean_thresholds_ - 3*std_thresholds_,0) or A.threshold==0:
            A.threshold = mean_thresholds_

        
    
    def setup_distributions(self, number_of_distributions):
        """
        Setup the distributions based on the number of distributions.
        """
        if number_of_distributions < 2:
            raise ValueError("Number of distributions must be at least 2.")
        # Generate distribution keys: "A".."Z", "AA".."AZ", "BA".."BZ", ...
        def generate_keys(n):
            keys = []
            alphabet = list(string.ascii_uppercase)
            # Single letters
            for c in alphabet:
                keys.append(c)
                if len(keys) == n:
                    return keys
            # Double letters, triple letters, etc.
            length = 2
            while len(keys) < n:
                for chars in np.ndindex(*(len(alphabet),) * length):
                    key = ''.join(alphabet[i] for i in chars)
                    keys.append(key)
                    if len(keys) == n:
                        return keys
                length += 1
            return keys

        distribution_keys = generate_keys(number_of_distributions)
        distributions = {k: None for k in distribution_keys}


        # Use a set of visually distinct colors (ColorBrewer + Tableau + some handpicked)
        color_list = [
            "#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf",  # ColorBrewer Set1
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",  # Tableau 10
            "#bcbd22", "#17becf", "#aec7e8", "#ffbb78", "#98df8a", "#c5b0d5", "#c49c94", "#f7b6d2",
            "#dbdb8d", "#9edae5", "#b15928", "#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854",  # ColorBrewer Set2
            "#ffd92f", "#e5c494", "#b3b3b3", "#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e",
            "#e6ab02", "#a6761d", "#666666", "#f0027f", "#bf5b17", "#a6cee3", "#b2df8a", "#fb9a99",
            "#fdbf6f", "#cab2d6", "#ffff99", "#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e"
        ]
        # Assign colors (reuse from key_colors if more keys than colors)
        key_colors = {k: color_list[i % len(color_list)] for i, k in enumerate(distribution_keys)}
        return distributions, key_colors
    
