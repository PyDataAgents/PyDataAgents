import enum


class DataType(str, enum.Enum):
    
    STRING = "STRING"
    NUMERIC = "NUMERIC"
    OBJECT = "OBJECT"
    IMAGE = "IMAGE"
    BYTE = "BYTE"
    