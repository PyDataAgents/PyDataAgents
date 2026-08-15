# Agents Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`AgentElement`](#agentelement-in-pydagagentsagentelementpy) | Abstract base class for agent elements. |



## `AgentElement` (in `pydag\agents\AgentElement.py`)

Abstract base class for agent elements.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `<dataclasses._MISSING_TYPE object at 0x00000223B3EED370>` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |
| `type` | `str` | `` | fully qualified package and class name descriptor |
| `id` | `str` | `'lambda: str(uuid.uuid4())()'` | unique identifier of element in DataAgent application |
| `load_on_install` | `bool` | `False` | specifies whether the AgentElement should try to load from local json config file on install |


```python
# Example usage of `AgentElement`
from pydag.agents.AgentElement import AgentElement  # Adjust import if needed

obj = AgentElement()
obj.id=<dataclasses._MISSING_TYPE object at 0x00000223B3EED370>
obj.load_on_install=False
obj.type="<string>"
obj.id='lambda: str(uuid.uuid4())()'
obj.load_on_install=False
```

[Go to Summary](#summary)