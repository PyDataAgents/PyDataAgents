from dataclasses import dataclass, field
from sktime.datasets import load_UCR_UEA_dataset
import numpy as np
import pandas as pd
import os

from pydag.agents.AgentConfig import AgentConfig

from ..buffers.BufferException import BufferException
from ..agents.Agent import Agent
from ..agents.AgentConfig import AgentConfig
from .DictBuffer import DictBuffer
from ..nodes.dataset.DatasetNames import DatasetNames


@dataclass
class DatasetBuffer(DictBuffer):
    """ A `Buffer` that loads a dataset and stores it in its elements
    """
    
    dataset_name : str = field(default=DatasetNames.Blobs.value, metadata={"description": """Dataset names. Tested are:
                                                                                ArrowHead: https://www.timeseriesclassification.com/description.php?Dataset=ArrowHead,
                                                                                AbnormalHeartbeat: https://www.timeseriesclassification.com/description.php?Dataset=AbnormalHeartbeat,
                                                                                Car: https://www.timeseriesclassification.com/description.php?Dataset=Car,
                                                                                ChlorineConcentration: https://www.timeseriesclassification.com/description.php?Dataset=ChlorineConcentration,
                                                                                Crop: https://www.timeseriesclassification.com/description.php?Dataset=Crop,
                                                                                ECG5000: https://www.timeseriesclassification.com/description.php?Dataset=ECG5000,
                                                                                ElectricDevices: https://www.timeseriesclassification.com/description.php?Dataset=ElectricDevices,
                                                                                FordA: https://www.timeseriesclassification.com/description.php?Dataset=FordA,
                                                                                InsectSound: https://www.timeseriesclassification.com/description.php?Dataset=InsectSound,
                                                                                KeplerLightCurves: https://www.timeseriesclassification.com/description.php?Dataset=KeplerLightCurves,
                                                                                Plane: https://www.timeseriesclassification.com/description.php?Dataset=Plane,
                                                                                ShapesAll: https://www.timeseriesclassification.com/description.php?Dataset=ShapesAll,
                                                                                UWaveGestureLibrary:https://www.timeseriesclassification.com/description.php?Dataset=UWaveGestureLibrary,
                                                                                Wafer: https://www.timeseriesclassification.com/description.php?Dataset=Wafer,
                                                                                Wine: https://www.timeseriesclassification.com/description.php?Dataset=Wine,
                                                                                Blobs: This is a sklearn dataset which creates Clusters. https://scikit-learn.org/stable/modules/generated/sklearn.datasets.make_blobs.html 
                                                                                CNC: This is a dataset from a publication which contains vibration measuremens from a CNC machine. The dataset is available at: https://archive.ics.uci.edu/dataset/752/bosch+cnc+machining+dataset and https://github.com/boschresearch/CNC_Machining. As mentioned on https://github.com/boschresearch/CNC_Machining please cite the following paper if you use the dataset: Tnani, Mohamed-Ali; Feil, Michael; Diepold, Klaus. Smart Data Collection System for Brownfield CNC Milling Machines: A New Benchmark Dataset for Data-Driven Machine Monitoring. Procedia CIRP2022,107, 131–136. Only datasets with "DE", "FE" and "BA" data is used.
                                                                                CWRU: The dataset is available at: https://github.com/srigas/CWRU_Bearing_NumPy and originally from https://engineering.case.edu/bearingdatacenter to where you should refer if you use the dataset.      
                                                                                You can test other datasets from https://www.timeseriesclassification.com/dataset.php as well but they are not tested yet."""})
        
    sort_by_y : bool = field(default=False, metadata={"description": "whether to sort the data by the labels y."})
    
    
    
    def install(self, agent : Agent = None):
        super().install()
        data = {}
        X : pd.DataFrame = None
        y : np.ndarray = None
        self.capacity = AgentConfig.INFINITE_CAPACITY
        
        # this directory should contain raw data files depending on the dataset
        resource_dir : str = os.getcwd() + os.sep + "resources"

        #set the capacity to infinite
        self.capacity = AgentConfig.INFINITE_CAPACITY
        
        if self.dataset_name == "Blobs":
            from sklearn.datasets import make_blobs
            X, y = make_blobs(
                                n_samples=[500, 500, 500, 500],
                                centers=[(0,0), (2,2), (7,7), (8,8)],  # manually set centers closer or farther
                                cluster_std=[1, 1.3, 3, 0.2],                # more spread → more overlap
                                random_state=42
                            )
            #import matplotlib.pyplot as plt
            #plt.scatter(X[:, 0], X[:, 1], c=y, cmap='viridis')
            #plt.show()
            ar_shape = X.shape[-1] # get the shape of the last dimension
            y = np.repeat(y, ar_shape)
            far = X.reshape(-1)
            fary = y.reshape(-1)
        

        elif self.dataset_name == "CNC":
            file_paths = []
            for file in os.listdir(os.path.join(resource_dir, "inputs", "BOSCH_CNC")):
                if file.endswith(".csv"):
                    file_paths.append(os.path.join(resource_dir, "inputs", "BOSCH_CNC", file))

            combined_datasets = pd.DataFrame()
            for file_path in file_paths:
                df = pd.read_csv(file_path, delimiter=";")
                combined_datasets = pd.concat([combined_datasets, df], ignore_index=True)
            unique, fary = np.unique(combined_datasets.pop("LABEL").to_numpy(), return_inverse=True)
            far = combined_datasets.to_numpy().T

            if self.sort_by_y:
                try:
                    fary = pd.to_numeric(fary)  # Convert y values to numeric if possible
                    perm = np.argsort(fary, kind='mergesort')   # stable: preserves order inside each label
                    
                    for dim in range(far.shape[0]):
                        data["values_{0}".format(dim)] = far[dim][perm].tolist()
                    data["y"] = fary[perm].tolist()
                except ValueError:
                    # If conversation fails, throw error
                    raise ValueError("y values could not be converted to numeric values. Sorting not possible.")
                else:
                    for dim in range(far.shape[0]):
                        data["values_{0}".format(dim)] = far[dim].tolist()
                    data["y"] = fary.tolist()
            # Subsample data by factor of 10 to reduce size
            for key in data.keys():
                    data[key] = data[key][::10]
            
            
        
        elif self.dataset_name == "CWRU":

            file_paths = []
            for file in os.listdir(os.path.join(resource_dir, "inputs", "CWRU_Bearing", "Data")):
                if file.endswith(".npz"):
                    file_paths.append(os.path.join(resource_dir, "inputs", "CWRU_Bearing", "Data", file))

            combined_datasets = pd.DataFrame()
            file_path : str
            for file_path in file_paths:
                dnpz = np.load(file_path)
                if not ("DE" in dnpz.files and "FE" in dnpz.files and "BA" in dnpz.files):
                    continue
                else:
                    df = pd.DataFrame(dnpz["DE"])
                    df["FE"] = dnpz["FE"]
                    df["BA"] = dnpz["BA"]
                    df["LABEL"] = file_path.split("\\")[-1].replace(".npz","")
                    combined_datasets = pd.concat([combined_datasets, df], ignore_index=True)
            unique, fary = np.unique(combined_datasets.pop("LABEL").to_numpy(), return_inverse=True)
            far = combined_datasets.to_numpy().T

            if self.sort_by_y:
                try:
                    fary = pd.to_numeric(fary)  # Convert y values to numeric if possible
                    perm = np.argsort(fary, kind='mergesort')   # stable: preserves order inside each label
                    
                    for dim in range(far.shape[0]):
                        data["values_{0}".format(dim)] = far[dim][perm].tolist()
                    data["y"] = fary[perm].tolist()
                except ValueError:
                    # If conversation fails, throw error
                    raise ValueError("y values could not be converted to numeric values. Sorting not possible.")
                else:
                    for dim in range(far.shape[0]):
                        data["values_{0}".format(dim)] = far[dim].tolist()
                    data["y"] = fary.tolist()
            
            
            
               
        else:
            X, y = load_UCR_UEA_dataset(name=self.dataset_name)
            d = X.to_dict(orient="list") # convert dataframe to dict
            dv = d.values() # extract values from dict
            dl = list(dv) # convert values to list
            ar = np.array(dl) # convert list to numpy array
            ar_shape = ar.shape[-1] # get the shape of the last dimension
            y = np.repeat(y, ar_shape)
            far = ar.reshape(-1) # flatten the array    
            fary = y.reshape(-1) # flatten the array    
        
            if self.sort_by_y:
                try:
                    fary = pd.to_numeric(fary)  # Convert y values to numeric if possible
                    perm = np.argsort(fary, kind='mergesort')   # stable: preserves order inside each label
                    data["values"] = far[perm].tolist()
                    data["y"] = fary[perm].tolist()
                except ValueError:
                    # If conversation fails, throw error
                    raise ValueError("y values could not be converted to numeric values. Sorting not possible.")
            else:
                data["values"] = far.tolist()
                data["y"] = fary.tolist()
           
            
        
        # Push to buffer
        self.push(data)

        