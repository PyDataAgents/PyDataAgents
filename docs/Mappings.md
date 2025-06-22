# Mappings Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Mapping`](#mapping-from-Mapping) |  |
| [`MappingObserver`](#mappingobserver-from-MappingObserver) | abstract base class for mapping observers |
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
    
_No fields defined._

## `MappingThread` (from `MappingThread.py`)

_No fields defined._

## `Observer` (from `Observer.py`)

_No fields defined._

## `ObserverThread` (from `ObserverThread.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `SAFETY_DIFF_TIME_UNITS` | `int` | `` |  |
| `SLEEP_WITH_HOLD_FACTOR` | `float` | `` |  |


```python
# Example usage of `ObserverThread`
from pydatagrabber import ObserverThread  # Adjust import if needed

obj = ObserverThread(
    SAFETY_DIFF_TIME_UNITS=1,
    SLEEP_WITH_HOLD_FACTOR=3.14
)
```

## `PublishMappingObserver` (from `PublishMappingObserver.py`)

_No fields defined._

## `ReadMappingObserver` (from `ReadMappingObserver.py`)

_No fields defined._

## `SubscribeMappingObserver` (from `SubscribeMappingObserver.py`)

_No fields defined._

## `WriteMappingObserver` (from `WriteMappingObserver.py`)

_No fields defined._
