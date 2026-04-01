from dataclasses import fields, is_dataclass
from typing import Any, Union, get_args, get_origin
import mimetypes
import base64
import os
import numpy as np
import pandas as pd
from loguru import logger 


class DataUtils:
    
    @staticmethod
    def dict_to_list(data : dict) -> list[dict]:
        """
        turns a column style dictionary data layout into a row style list of dictionaries

        Args:
            data (dict): dictionary with column style data content

        Returns:
            list[dict]: list of dictionaries (row-style)
        """
        if data is None:
            return None
        return [dict(zip(data.keys(), values)) for values in zip(*data.values())]
    
    @staticmethod
    def list_to_dict(data : list) -> dict:
        """
        turns a row style data layout into a column style dictionary of lists
        Args:
            data (list): list of dictionaries

        Returns:
            dict: _descdictionary of lists
        """
        if data is None:
            return None
        return {key: [d[key] for d in data] for key in data[0].keys()}
    
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
    
    @staticmethod            
    def dict_to_obj(cls, data : dict) -> object:
        """ generate an object from dictionary, also attempting to recreate nested object hierarchies

        Args:
            cls (Any): class to create
            data (dict): serialized object data as dictionary

        Returns:
            object: object of cls
        """
        if not is_dataclass(cls):
            raise TypeError(f"{cls} is not a dataclass")

        kwargs = {}
        for field in fields(cls):
            value = data.get(field.name)
            if value is None:
                kwargs[field.name] = None
                continue

            field_type = field.type
            origin = get_origin(field_type)

            # Handle Optional
            if origin is Union:
                args = get_args(field_type)
                non_none = [arg for arg in args if arg is not type(None)]
                field_type = non_none[0]
                origin = get_origin(field_type)

            # Handle list of nested dataclasses
            if origin == list:
                inner_type = get_args(field_type)[0]
                kwargs[field.name] = [DataUtils.dict_to_obj(inner_type, item) if isinstance(item, dict) else item for item in value]

            # Nested dataclass
            elif is_dataclass(field_type) and isinstance(value, dict):
                kwargs[field.name] = DataUtils.dict_to_obj(field_type, value)

            else:
                kwargs[field.name] = value

        return cls(**kwargs)
        
    @staticmethod
    def image_to_base64(image_path: str) -> str:
        """Encodes an image file to a Base64 data URL."""
        if not os.path.isfile(image_path):
            logger.debug(f"File not found: {image_path}")
            return None
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None:
            logger.debug(f"Could not determine MIME type for file: {image_path}")
            return None
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            data_url = f"data:{mime_type};base64,{encoded_string}"
            return data_url
    
    @staticmethod
    def serialize_dict(data : dict):
        """force all data or objects contained in `data` to be in serialized data structure.
        e.g. if numpy arrays are present they are converted to lists
        """
        for k, v in data.items():
            if isinstance(v, list):
                if len(v) > 0:
                    if isinstance(v[0], np.ndarray):
                        for i, item in enumerate(v):
                            v[i] = item.tolist()
            if isinstance(v, np.ndarray):
                data[k] = v.tolist()
        
        return data
    
    @staticmethod
    def is_numeric(value : Any) -> bool:
        """ checks whether given object is numeric by parsing to float

        Args:
            value (Any): any object

        Returns:
            bool: True/False
        """
        try:
            float(value)  # Try converting to float
            return True
        except ValueError:
            return False
    
    @staticmethod 
    def is_numeric_type(value : Any) -> bool:
        """ checks whether given `value` is of a numeric type (`int`  or `float`)

        Args:
            value (Any): any object

        Returns:
            bool: True/False
        """
        if isinstance(value, (int, float)):
            return True
        else:
            return False
        
    @staticmethod
    def replace_nan(data : dict[str, Any], nan_value : float = 0.0, posinf_value : float = 0.0, neginf_value : float = 0.0) -> dict:
        cleaned : dict[str, Any] = {}
        for k, v in data.items():
            arr = np.asarray(v)
            if not np.isfinite(arr).all():
                arr = np.nan_to_num(arr, nan=nan_value, posinf=posinf_value, neginf=neginf_value)
            cleaned[k] = arr.tolist() if not np.isscalar(arr) else list(arr)
        return cleaned

        
        