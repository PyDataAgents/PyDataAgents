import enum  


class Comparator(str, enum.Enum):
    """
    Enum for different types of comparators.
    """
    
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    GREATER = "GREATER"
    LESS = "LESS"
    EQUAL_OR_GREATER = "EQUAL_OR_GREATER"
    EQUAL_OR_LESS = "EQUAL_OR_LESS"
    LIKE = "LIKE"
    NOT_LIKE = "NOT_LIKE"
    NOT_NULL = "NOT_NULL"