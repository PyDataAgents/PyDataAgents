import enum


class MappingType(enum.Enum):
    READ = "READ"
    WRITE = "WRITE"
    SUB = "SUB"
    PUB = "PUB"