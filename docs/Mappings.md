# Mappings Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Mapping`](#mapping-in-pydagmappingsmappingpy) |      |
| [`MappingObserver`](#mappingobserver-in-pydagmappingsmappingobserverpy) | abstract base class for mapping observers     |
| [`MappingThread`](#mappingthread-in-pydagmappingsmappingthreadpy) |  |
| [`Observer`](#observer-in-pydagmappingsobserverpy) |  |
| [`ObserverThread`](#observerthread-in-pydagmappingsobserverthreadpy) |  |
| [`PublishMappingObserver`](#publishmappingobserver-in-pydagmappingspublishmappingobserverpy) |  |
| [`ReadMappingObserver`](#readmappingobserver-in-pydagmappingsreadmappingobserverpy) |  |
| [`SubscribeMappingObserver`](#subscribemappingobserver-in-pydagmappingssubscribemappingobserverpy) |  |
| [`WriteMappingObserver`](#writemappingobserver-in-pydagmappingswritemappingobserverpy) |  |



## `Mapping` (in `pydag\mappings\Mapping.py`)

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `buffer_ids` | `list[str]` | `` | list of buffer ids to map from |
| `adapter_id` | `str` | `` | id of the Adapter used for this Mapping |
| `addresses` | `list[str]` | `'list()'` | list of addresses to read/subscribe from or write/publish to |
| `thread_type` | `str` | `'ThreadType.MILLI_SECOND.value'` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, ... |
| `mapping_type` | `str` | `` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `1` | number of samples to insert or remove from buffers |
| `sampling_period` | `int` | `100` | sampling period to apply in this Mapping |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with agent start |


```python
# Example usage of `Mapping`
from pydag.mappings.Mapping import Mapping  # Adjust import if needed

obj = Mapping()
obj.id="<string>"
obj.load_on_install=False
obj.buffer_ids="<string>"
obj.adapter_id="<string>"
obj.addresses='list()'
obj.thread_type='ThreadType.MILLI_SECOND.value'
obj.mapping_type="<string>"
obj.n=1
obj.sampling_period=100
obj.persistent=True
obj.auto_start=True
```

[Go to Summary](#summary)
## `MappingObserver` (in `pydag\mappings\MappingObserver.py`)

abstract base class for mapping observers
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `MappingObserver`
from pydag.mappings.MappingObserver import MappingObserver  # Adjust import if needed

obj = MappingObserver()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `MappingThread` (in `pydag\mappings\MappingThread.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `MappingThread`
from pydag.mappings.MappingThread import MappingThread  # Adjust import if needed

obj = MappingThread()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `Observer` (in `pydag\mappings\Observer.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Observer`
from pydag.mappings.Observer import Observer  # Adjust import if needed

obj = Observer()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `ObserverThread` (in `pydag\mappings\ObserverThread.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `sampling_period` | `int` | `0` | sampling period between observer notifies |
| `thread_type` | `str` | `'ThreadType.MILLI_SECOND.value'` | type of thread -> MILLI_SECOND | MICRO_SECOND | NANO_SECOND | SECOND | ONLY_ONCE | INSTANT | TRIGGERED |
| `SAFETY_DIFF_TIME_UNITS` | `float` | `` |  |
| `SLEEP_WITH_HOLD_FACTOR` | `float` | `` |  |


```python
# Example usage of `ObserverThread`
from pydag.mappings.ObserverThread import ObserverThread  # Adjust import if needed

obj = ObserverThread()
obj.id="<string>"
obj.load_on_install=False
obj.sampling_period=0
obj.thread_type='ThreadType.MILLI_SECOND.value'
obj.SAFETY_DIFF_TIME_UNITS=3.14
obj.SLEEP_WITH_HOLD_FACTOR=3.14
```

[Go to Summary](#summary)
## `PublishMappingObserver` (in `pydag\mappings\PublishMappingObserver.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `PublishMappingObserver`
from pydag.mappings.PublishMappingObserver import PublishMappingObserver  # Adjust import if needed

obj = PublishMappingObserver()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `ReadMappingObserver` (in `pydag\mappings\ReadMappingObserver.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `ReadMappingObserver`
from pydag.mappings.ReadMappingObserver import ReadMappingObserver  # Adjust import if needed

obj = ReadMappingObserver()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `SubscribeMappingObserver` (in `pydag\mappings\SubscribeMappingObserver.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `SubscribeMappingObserver`
from pydag.mappings.SubscribeMappingObserver import SubscribeMappingObserver  # Adjust import if needed

obj = SubscribeMappingObserver()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `WriteMappingObserver` (in `pydag\mappings\WriteMappingObserver.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `WriteMappingObserver`
from pydag.mappings.WriteMappingObserver import WriteMappingObserver  # Adjust import if needed

obj = WriteMappingObserver()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)