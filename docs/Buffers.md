# Buffers Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Buffer`](#buffer-from-Buffer) | Abstract base class for buffers. |
| [`DictBuffer`](#dictbuffer-from-DictBuffer) | buffer that stores its values in a dictionary in a table like fashion, where every key contains a list of data
     |
| [`ListBuffer`](#listbuffer-from-ListBuffer) | buffer that stores its values in a capacity limited list
     |
| [`ObjectTransformation`](#objecttransformation-from-ObjectTransformation) | Abstract base class for object transformations for buffers |
| [`SampledBuffer`](#sampledbuffer-from-SampledBuffer) | A buffer that samples a signal at a specified interval. |
| [`SignalBuffer`](#signalbuffer-from-SignalBuffer) | A buffer that holds signals with a specific start time and elapsed time.

Attributes:
    start_time (int): The start time of the signal in milliseconds.
    elapsed_time (float): The elapsed time since the start in seconds. |
| [`TimedBuffer`](#timedbuffer-from-TimedBuffer) | A buffer that stores data with timestamps.
Inherits from ListBuffer. |
| [`TransformsBuffer`](#transformsbuffer-from-TransformsBuffer) | TransformsBuffer is a subclass of ListBuffer that allows for data transformation.
It is used to transform data from one format to another. |
| [`SampledSignal`](#sampledsignal-from-signals\SampledSignal) | A class representing a sampled signal for continuously sampled data |
| [`SampledSine`](#sampledsine-from-signals\SampledSine) | A class to represent a sampled sine wave signal.

Attributes:
    f (float): The frequency of the sine wave in Hz.
    a (float): The amplitude of the sine wave.
    sample_rate (int): The number of samples per second.
    p (float): The phase of the sine wave in °. |
| [`Signal`](#signal-from-signals\Signal) | Abstract base class for signals. |
| [`Sine`](#sine-from-signals\Sine) | A class to represent a sine wave signal. |
| [`ClippingTransformation`](#clippingtransformation-from-transformations\ClippingTransformation) |  |



## `Buffer` (from `Buffer.py`)

Abstract base class for buffers.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |


```python
# Example usage of `Buffer`
from pydatagrabber import Buffer  # Adjust import if needed

obj = Buffer(
    id="<string>",
    load_on_install=False,
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>"
)
```

## `DictBuffer` (from `DictBuffer.py`)

buffer that stores its values in a dictionary in a table like fashion, where every key contains a list of data
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `DictBuffer`
from pydatagrabber import DictBuffer  # Adjust import if needed

obj = DictBuffer(
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>",
    id="<string>",
    load_on_install=False
)
```

## `ListBuffer` (from `ListBuffer.py`)

buffer that stores its values in a capacity limited list
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `ListBuffer`
from pydatagrabber import ListBuffer  # Adjust import if needed

obj = ListBuffer(
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>",
    id="<string>",
    load_on_install=False
)
```

## `ObjectTransformation` (from `ObjectTransformation.py`)

Abstract base class for object transformations for buffers
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `datatype` | `str` | `'DataType.FLOAT.value'` | type of data expected for the transform |


```python
# Example usage of `ObjectTransformation`
from pydatagrabber import ObjectTransformation  # Adjust import if needed

obj = ObjectTransformation(
    id="<string>",
    load_on_install=False,
    datatype='DataType.FLOAT.value'
)
```

## `SampledBuffer` (from `SampledBuffer.py`)

A buffer that samples a signal at a specified interval.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `SampledBuffer`
from pydatagrabber import SampledBuffer  # Adjust import if needed

obj = SampledBuffer(
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>",
    id="<string>",
    load_on_install=False
)
```

## `SignalBuffer` (from `SignalBuffer.py`)

A buffer that holds signals with a specific start time and elapsed time.

Attributes:
    start_time (int): The start time of the signal in milliseconds.
    elapsed_time (float): The elapsed time since the start in seconds.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `signal` | `Signal` | `` | a signal object to simulate data |
| `sampling_period` | `int` | `100` | interval in milliseconds for update |


```python
# Example usage of `SignalBuffer`
from pydatagrabber import SignalBuffer  # Adjust import if needed

obj = SignalBuffer(
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>",
    id="<string>",
    load_on_install=False,
    signal="<value>",
    sampling_period=100
)
```

## `TimedBuffer` (from `TimedBuffer.py`)

A buffer that stores data with timestamps.
Inherits from ListBuffer.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `TimedBuffer`
from pydatagrabber import TimedBuffer  # Adjust import if needed

obj = TimedBuffer(
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>",
    id="<string>",
    load_on_install=False
)
```

## `TransformsBuffer` (from `TransformsBuffer.py`)

TransformsBuffer is a subclass of ListBuffer that allows for data transformation.
It is used to transform data from one format to another.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | number of elements that can be stored in buffer before being discarded in FiFo fashion |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `transformations` | `list[ObjectTransformation]` | `[]` | List of transformations to apply to the data |


```python
# Example usage of `TransformsBuffer`
from pydatagrabber import TransformsBuffer  # Adjust import if needed

obj = TransformsBuffer(
    capacity=1,
    data_type='DataType.FLOAT.value',
    initial_values="<value>",
    unit="<value>",
    description="<string>",
    id="<string>",
    load_on_install=False,
    transformations=[]
)
```

## `SampledSignal` (from `signals\SampledSignal.py`)

A class representing a sampled signal for continuously sampled data
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `sample_rate` | `float` | `1.0` | sample rate of the signal in Hz |


```python
# Example usage of `SampledSignal`
from pydatagrabber import SampledSignal  # Adjust import if needed

obj = SampledSignal(
    id="<string>",
    load_on_install=False,
    sample_rate=1.0
)
```

## `SampledSine` (from `signals\SampledSine.py`)

A class to represent a sampled sine wave signal.

Attributes:
    f (float): The frequency of the sine wave in Hz.
    a (float): The amplitude of the sine wave.
    sample_rate (int): The number of samples per second.
    p (float): The phase of the sine wave in °.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sample_rate` | `float` | `1.0` | sample rate of the signal in Hz |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `f` | `float` | `1.0` | frequency of sine wave in Hz |
| `a` | `float` | `1.0` | amplitude of sine wave |
| `p` | `float` | `0.0` | phase angle of sine wave in ° |
| `n` | `float` | `0.0` | noise level of sine wave in respect to ampltidue [0..1] |


```python
# Example usage of `SampledSine`
from pydatagrabber import SampledSine  # Adjust import if needed

obj = SampledSine(
    sample_rate=1.0,
    id="<string>",
    load_on_install=False,
    f=1.0,
    a=1.0,
    p=0.0,
    n=0.0
)
```

## `Signal` (from `signals\Signal.py`)

Abstract base class for signals.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Signal`
from pydatagrabber import Signal  # Adjust import if needed

obj = Signal(
    id="<string>",
    load_on_install=False
)
```

## `Sine` (from `signals\Sine.py`)

A class to represent a sine wave signal.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `f` | `float` | `1.0` | frequency of sine wave in Hz |
| `a` | `float` | `1.0` | amplitude of sine wave |
| `p` | `float` | `0.0` | phase angle of sine wave in ° |
| `n` | `float` | `0.0` | noise level of sine wave in respect to ampltidue [0..1] |


```python
# Example usage of `Sine`
from pydatagrabber import Sine  # Adjust import if needed

obj = Sine(
    id="<string>",
    load_on_install=False,
    f=1.0,
    a=1.0,
    p=0.0,
    n=0.0
)
```

## `ClippingTransformation` (from `transformations\ClippingTransformation.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `datatype` | `str` | `'DataType.FLOAT.value'` | type of data expected for the transform |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `lower_limit` | `float` | `0.0` | lower limit for clipping |
| `upper_limit` | `float` | `1.0` | upper limit for clipping |


```python
# Example usage of `ClippingTransformation`
from pydatagrabber import ClippingTransformation  # Adjust import if needed

obj = ClippingTransformation(
    datatype='DataType.FLOAT.value',
    id="<string>",
    load_on_install=False,
    lower_limit=0.0,
    upper_limit=1.0
)
```
