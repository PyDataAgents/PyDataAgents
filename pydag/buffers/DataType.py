import enum


class DataType(str, enum.Enum):
    
    def __new__(cls, value: str, byte_size: int | None):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.byte_size = byte_size
        return obj
    
    STRING = ("STRING", None)   # Variable length
    FLOAT  = ("FLOAT", 8)       # 8 bytes (double precision)
    INT    = ("INT", 4)         # 4 bytes (int32)
    OBJECT = ("OBJECT", None)   # Depends on object
    IMAGE  = ("IMAGE", None)    # Depends on resolution/format
    BYTE   = ("BYTE", 1)        # 1 byte
    BOOL   = ("BOOL", 1)        # 1 byte
 