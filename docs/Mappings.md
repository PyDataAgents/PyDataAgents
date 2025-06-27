# Mappings Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Mapping`](#mapping-from-Mapping) |      |
| [`MappingObserver`](#mappingobserver-from-MappingObserver) | abstract base class for mapping observers     |
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

obj = Mapping()
obj.id="<string>"
obj.load_on_install=False
obj.buffer_ids="<string>"
obj.adapter_id="<string>"
obj.addresses="<string>"
obj.thread_type='ThreadType.MILLI_SECOND.value'
obj.mapping_type="<string>"
obj.n=1
obj.sampling_period=100
obj.persistent=True
obj.auto_start=True
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

obj = MappingObserver()
obj.id="<string>"
obj.load_on_install=False
```

## `MappingThread` (from `MappingThread.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `MappingThread`
from pydatagrabber import MappingThread  # Adjust import if needed

obj = MappingThread()
obj.id="<string>"
obj.load_on_install=False
```

## `Observer` (from `Observer.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Observer`
from pydatagrabber import Observer  # Adjust import if needed

obj = Observer()
obj.id="<string>"
obj.load_on_install=False
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

obj = ObserverThread()
obj.id="<string>"
obj.load_on_install=False
obj.SAFETY_DIFF_TIME_UNITS=1
obj.SLEEP_WITH_HOLD_FACTOR=3.14
```

## `PublishMappingObserver` (from `PublishMappingObserver.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `PublishMappingObserver`
from pydatagrabber import PublishMappingObserver  # Adjust import if needed

obj = PublishMappingObserver()
obj.id="<string>"
obj.load_on_install=False
```

## `ReadMappingObserver` (from `ReadMappingObserver.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `ReadMappingObserver`
from pydatagrabber import ReadMappingObserver  # Adjust import if needed

obj = ReadMappingObserver()
obj.id="<string>"
obj.load_on_install=False
```

## `SubscribeMappingObserver` (from `SubscribeMappingObserver.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `SubscribeMappingObserver`
from pydatagrabber import SubscribeMappingObserver  # Adjust import if needed

obj = SubscribeMappingObserver()
obj.id="<string>"
obj.load_on_install=False
```

## `WriteMappingObserver` (from `WriteMappingObserver.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `WriteMappingObserver`
from pydatagrabber import WriteMappingObserver  # Adjust import if needed

obj = WriteMappingObserver()
obj.id="<string>"
obj.load_on_install=False
```
