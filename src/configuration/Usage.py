from dataclasses import dataclass


def Usage(description : str):
    def wrapper(cls):
        cls = dataclass(cls)
        cls.__description__ = description
        return cls
    return wrapper