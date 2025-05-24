import enum


class DataType(str, enum.Enum):
    
    STRING = "STRING"
    FLOAT = "FLOAT"
    INT = "INT"
    OBJECT = "OBJECT"
    IMAGE = "IMAGE"
    BYTE = "BYTE"
    BOOL = "BOOL"    