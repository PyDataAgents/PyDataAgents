# Agents Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Agent`](#agent-in-pydagagentsagentpy) |  |



## `Agent` (in `pydag\agents\Agent.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `str` | `` | fully qualified package and class name descriptor |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Agent`
from pydag.agents.Agent import Agent  # Adjust import if needed

obj = Agent()
obj.type="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)