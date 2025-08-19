# Agents Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Agent`](#agent-in-pydagagentsagentpy) |  |
| [`AgentElement`](#agentelement-in-pydagagentsagentelementpy) | Abstract base class for agent elements. |



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
## `AgentElement` (in `pydag\agents\AgentElement.py`)

Abstract base class for agent elements.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `type` | `str` | `` | fully qualified package and class name descriptor |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `AgentElement`
from pydag.agents.AgentElement import AgentElement  # Adjust import if needed

obj = AgentElement()
obj.id="<string>"
obj.load_on_install=False
obj.type="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)