
import random


def hello(name) -> str:
    return f"Hello {name}"

def goodbye(name) -> str:
    return f"let's meet some other time, {name}"

def count(s : str) -> int:
    return len(s)

def rands() -> tuple[int, int]:
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    return a, b