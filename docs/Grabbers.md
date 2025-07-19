# Grabbers Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Grabber`](#grabber-in-pydggrabbersgrabberpy) |  |



## `Grabber` (in `pydg\grabbers\Grabber.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `str` | `` | fully qualified package and class name descriptor |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Grabber`
from pydg.grabbers.Grabber import Grabber  # Adjust import if needed

obj = Grabber()
obj.type="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)