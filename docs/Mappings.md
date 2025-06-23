# Mappings Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Mapping`](#mapping-from-Mapping) |      |
| [`MappingObserver`](#mappingobserver-from-MappingObserver) | abstract base class for mapping observers
     |
| [`MappingThread`](#mappingthread-from-MappingThread) |  |
| [`Observer`](#observer-from-Observer) |  |
| [`ObserverThread`](#observerthread-from-ObserverThread) |  |
| [`PublishMappingObserver`](#publishmappingobserver-from-PublishMappingObserver) |  |
| [`ReadMappingObserver`](#readmappingobserver-from-ReadMappingObserver) |  |
| [`SubscribeMappingObserver`](#subscribemappingobserver-from-SubscribeMappingObserver) |  |
| [`WriteMappingObserver`](#writemappingobserver-from-WriteMappingObserver) |  |



## `Mapping` (from `Mapping.py`)

    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `buffer_ids` | `list[str]` | `` | list of buffer ids to map from |
| `adapter_id` | `str` | `` | id of the Adapter used for this Mapping |
| `addresses` | `list[str]` | `` | list of addresses to read/subscribe from or write/publish to |
| `thread_type` | `str` | `'ThreadType.MILLI_SECOND.value'` | type of thread, e.g. MILLI_SECONDS, MICRO_SECONDS, INSTANT, ONLY_ONCE, ... |
| `mapping_type` | `str` | `` | type of mapping, e.g. READ, WRITE, SUB or PUB |
| `n` | `int` | `1` | number of samples to insert or remove from buffers |
| `sampling_period` | `int` | `100` | sampling period to apply in this Mapping |
| `persistent` | `bool` | `True` | specifies whether to remove or keep the values of the buffers when writing or publishing to a data sink |
| `auto_start` | `bool` | `True` | specifies whether to start the mapping with grabber start |


```python
# Example usage of `Mapping`
from pydatagrabber import Mapping  # Adjust import if needed

obj = Mapping(
    id="<string>",
    load_on_install=False,
    buffer_ids="<string>",
    adapter_id="<string>",
    addresses="<string>",
    thread_type='ThreadType.MILLI_SECOND.value',
    mapping_type="<string>",
    n=1,
    sampling_period=100,
    persistent=True,
    auto_start=True
)
```

## `MappingObserver` (from `MappingObserver.py`)

abstract base class for mapping observers
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `MappingObserver`
from pydatagrabber import MappingObserver  # Adjust import if needed

obj = MappingObserver(
    id="<string>",
    load_on_install=False
)
```

## `MappingThread` (from `MappingThread.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `MappingThread`
from pydatagrabber import MappingThread  # Adjust import if needed

obj = MappingThread(
    id="<string>",
    load_on_install=False
)
```

## `Observer` (from `Observer.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Observer`
from pydatagrabber import Observer  # Adjust import if needed

obj = Observer(
    id="<string>",
    load_on_install=False
)
```

## `ObserverThread` (from `ObserverThread.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `SAFETY_DIFF_TIME_UNITS` | `int` | `` |  |
| `SLEEP_WITH_HOLD_FACTOR` | `float` | `` |  |


```python
# Example usage of `ObserverThread`
from pydatagrabber import ObserverThread  # Adjust import if needed

obj = ObserverThread(
    id="<string>",
    load_on_install=False,
    SAFETY_DIFF_TIME_UNITS=1,
    SLEEP_WITH_HOLD_FACTOR=3.14
)
```

## `PublishMappingObserver` (from `PublishMappingObserver.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `PublishMappingObserver`
from pydatagrabber import PublishMappingObserver  # Adjust import if needed

obj = PublishMappingObserver(
    id="<string>",
    load_on_install=False
)
```

## `ReadMappingObserver` (from `ReadMappingObserver.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `ReadMappingObserver`
from pydatagrabber import ReadMappingObserver  # Adjust import if needed

obj = ReadMappingObserver(
    id="<string>",
    load_on_install=False
)
```

## `SubscribeMappingObserver` (from `SubscribeMappingObserver.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `SubscribeMappingObserver`
from pydatagrabber import SubscribeMappingObserver  # Adjust import if needed

obj = SubscribeMappingObserver(
    id="<string>",
    load_on_install=False
)
```

## `WriteMappingObserver` (from `WriteMappingObserver.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `WriteMappingObserver`
from pydatagrabber import WriteMappingObserver  # Adjust import if needed

obj = WriteMappingObserver(
    id="<string>",
    load_on_install=False
)
```
