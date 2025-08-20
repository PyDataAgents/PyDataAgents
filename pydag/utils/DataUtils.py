import numpy as np
import pandas as pd
from typing import Any, Union


class DataUtils:
    
    @staticmethod
    def force_numeric(value):
        """_attempty to convert the given value into an int or float

        Args:
            value (any): any object

        Returns:
            _type_: returns a numeric value if possible otherwise the original object
        """
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value  # Keep as string if not numeric
            
    @staticmethod        
    def dict_to_ndarray(data: dict) -> np.ndarray:
        """
        Converts a dictionary to a NumPy ndarray.
        
        Args:
            data (dict): The input dictionary.
            
        Returns:
            np.ndarray: The converted NumPy ndarray.
        """
        return np.array(list(data.values()))

    @staticmethod
    def ndarray_to_dict(data: np.ndarray) -> dict:
        """
        Converts a NumPy ndarray to a dictionary.
        
        Args:
            data (np.ndarray): The input NumPy ndarray.
            
        Returns:
            dict: The converted dictionary.
        """
        if data.ndim == 1:
            return {"f0": data.tolist()}
        else:
            return {f"f{i}": data[i, :].tolist() for i in range(data.ndim)}
        
    @staticmethod
    def ndarray_to_list(data: np.ndarray, by_row : bool = False) -> list:
        """
        Converts a NumPy ndarray to a list.
        
        Args:
            data (np.ndarray): The input NumPy ndarray.
            
        Returns:
            list: The converted list.
        """
        if data.ndim > 1:            
            if data.ndim == 2:
                if by_row == False:
                    if data.shape[1] == 1:
                        return data.flatten().tolist()
            else:
                # TODO
                pass
        else:
            if by_row:
                # TODO
                pass
            else:        
                return data.tolist()
    
    @staticmethod    
    def list_to_ndarray(data : list) -> np.ndarray:
        """converts a list to a Numpy ndarray

        Args:
            data (list): list to convert

        Returns:
            np.ndarray: numpy array
        """
        return np.ndarray(data)
        
    @staticmethod
    def dataframe_to_dict(df : pd.DataFrame, by_row : bool = False) -> dict:
        if by_row:
            return df.to_dict(orient="records")  
        else:
            return df.to_dict(orient="list")
        
    @staticmethod
    def dict_to_dataframe(data : Union[list|dict], by_row : bool = False) -> pd.DataFrame:
        """converts list or dictionary data to a Pandas DataFrame

        Args:
            data (Union[list | dict]): list of dictionaries or dictionary
            by_row (bool, optional): specifies the form of the dictionary data, whether its row or column based. Defaults to False.

        Returns:
            pd.DataFrame: pd.DataFrame
        """
        if isinstance(data, list):
            df = df = pd.DataFrame.from_dict(data)
        else:
            if by_row:
                df = pd.DataFrame.from_dict(data, orient="index")
            else:
                df = pd.DataFrame.from_dict(data)
        return df
    
    @staticmethod
    def obj_to_dict(obj : Any, ignore_none : bool = True) -> dict:
        """ method recursively returns a nested dict structure of the entire obj

        Args:
            obj (Any): _description_    
            ignore_none (bool): if set to True, then properties / objects with 'None' value are ignored
                            
        Returns:
            dict: returns a dictionary
        """
        if isinstance(obj, dict):
            return {k: DataUtils.obj_to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [DataUtils.obj_to_dict(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            if ignore_none:
                return {k: DataUtils.obj_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith("_") and not v is None}
            else:
                return {k: DataUtils.obj_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
        else:
            if ignore_none:
                if obj is not None:
                    return obj
                else:
                    return