import enum


class MappingType(str, enum.Enum):
    READ = "READ"
    WRITE = "WRITE"
    SUB = "SUB"
    PUB = "PUB"