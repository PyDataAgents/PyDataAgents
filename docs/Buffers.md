# Buffers Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Buffer`](#buffer-in-pydagbuffersbufferpy) | Abstract base class for buffers. |
| [`DictBuffer`](#dictbuffer-in-pydagbuffersdictbufferpy) | buffer that stores its values in a dictionary in a table like fashion, where every key contains a list of data     |
| [`ListBuffer`](#listbuffer-in-pydagbufferslistbufferpy) | buffer that stores its values in a capacity limited list     |
| [`ObjectTransformation`](#objecttransformation-in-pydagbuffersobjecttransformationpy) | Abstract base class for object transformations for buffers |
| [`SampledBuffer`](#sampledbuffer-in-pydagbufferssampledbufferpy) | A buffer that samples a signal at a specified interval. |
| [`SignalBuffer`](#signalbuffer-in-pydagbufferssignalbufferpy) | A buffer that holds signals with a specific start time and elapsed time.Attributes:    start_time (int): The start time of the signal in milliseconds.    elapsed_time (float): The elapsed time since the start in seconds. |
| [`TimedBuffer`](#timedbuffer-in-pydagbufferstimedbufferpy) | A buffer that stores data with timestamps.Inherits from ListBuffer. |
| [`TransformsBuffer`](#transformsbuffer-in-pydagbufferstransformsbufferpy) | TransformsBuffer is a subclass of ListBuffer that allows for data transformation.It is used to transform data from one format to another. |
| [`LinearTrend`](#lineartrend-in-pydagbufferssignalslineartrendpy) | A signal that simulates a linear trend |
| [`SampledSignal`](#sampledsignal-in-pydagbufferssignalssampledsignalpy) | A class representing a sampled signal for continuously sampled data |
| [`SampledSine`](#sampledsine-in-pydagbufferssignalssampledsinepy) | A class to represent a sampled sine wave signal.Attributes:    f (float): The frequency of the sine wave in Hz.    a (float): The amplitude of the sine wave.    sample_rate (int): The number of samples per second.    p (float): The phase of the sine wave in °. |
| [`Signal`](#signal-in-pydagbufferssignalssignalpy) | Abstract base class for signals. |
| [`Sine`](#sine-in-pydagbufferssignalssinepy) | A class to represent a sine wave signal. |
| [`TimedSignal`](#timedsignal-in-pydagbufferssignalstimedsignalpy) | A signal that emits values at specified time intervals. |
| [`ClippingTransformation`](#clippingtransformation-in-pydagbufferstransformationsclippingtransformationpy) |  |



## `Buffer` (in `pydag\buffers\Buffer.py`)

Abstract base class for buffers.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `capacity` | `int` | `1` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |


```python
# Example usage of `Buffer`
from pydag.buffers.Buffer import Buffer  # Adjust import if needed

obj = Buffer()
obj.id="<string>"
obj.load_on_install=False
obj.capacity=1
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
```

[Go to Summary](#summary)
## `DictBuffer` (in `pydag\buffers\DictBuffer.py`)

buffer that stores its values in a dictionary in a table like fashion, where every key contains a list of data
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `DictBuffer`
from pydag.buffers.DictBuffer import DictBuffer  # Adjust import if needed

obj = DictBuffer()
obj.capacity=1
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `ListBuffer` (in `pydag\buffers\ListBuffer.py`)

buffer that stores its values in a capacity limited list
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `ListBuffer`
from pydag.buffers.ListBuffer import ListBuffer  # Adjust import if needed

obj = ListBuffer()
obj.capacity=1
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `ObjectTransformation` (in `pydag\buffers\ObjectTransformation.py`)

Abstract base class for object transformations for buffers
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `datatype` | `str` | `'DataType.FLOAT.value'` | type of data expected for the transform |


```python
# Example usage of `ObjectTransformation`
from pydag.buffers.ObjectTransformation import ObjectTransformation  # Adjust import if needed

obj = ObjectTransformation()
obj.id="<string>"
obj.load_on_install=False
obj.datatype='DataType.FLOAT.value'
```

[Go to Summary](#summary)
## `SampledBuffer` (in `pydag\buffers\SampledBuffer.py`)

A buffer that samples a signal at a specified interval.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `SampledBuffer`
from pydag.buffers.SampledBuffer import SampledBuffer  # Adjust import if needed

obj = SampledBuffer()
obj.capacity=1
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `SignalBuffer` (in `pydag\buffers\SignalBuffer.py`)

A buffer that holds signals with a specific start time and elapsed time.

Attributes:
    start_time (int): The start time of the signal in milliseconds.
    elapsed_time (float): The elapsed time since the start in seconds.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
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
from pydag.buffers.SignalBuffer import SignalBuffer  # Adjust import if needed

obj = SignalBuffer()
obj.capacity=1
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.signal="<value>"
obj.sampling_period=100
```

[Go to Summary](#summary)
## `TimedBuffer` (in `pydag\buffers\TimedBuffer.py`)

A buffer that stores data with timestamps.
Inherits from ListBuffer.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `TimedBuffer`
from pydag.buffers.TimedBuffer import TimedBuffer  # Adjust import if needed

obj = TimedBuffer()
obj.capacity=1
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `TransformsBuffer` (in `pydag\buffers\TransformsBuffer.py`)

TransformsBuffer is a subclass of ListBuffer that allows for data transformation.
It is used to transform data from one format to another.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `1` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `transformations` | `list[ObjectTransformation]` | `[]` | List of transformations to apply to the data |


```python
# Example usage of `TransformsBuffer`
from pydag.buffers.TransformsBuffer import TransformsBuffer  # Adjust import if needed

obj = TransformsBuffer()
obj.capacity=1
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.transformations=[]
```

[Go to Summary](#summary)
## `LinearTrend` (in `pydag\buffers\signals\LinearTrend.py`)

A signal that simulates a linear trend
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `min` | `float` | `0.0` | minimum value of the trend |
| `max` | `float` | `100.0` | maximum value of the trend |
| `duration` | `int` | `'1000 * 1000'` | duration of the trend in milliseconds |
| `noise` | `float` | `0.0` | noise to add to the trend [0..1] |


```python
# Example usage of `LinearTrend`
from pydag.buffers.signals.LinearTrend import LinearTrend  # Adjust import if needed

obj = LinearTrend()
obj.id="<string>"
obj.load_on_install=False
obj.min=0.0
obj.max=100.0
obj.duration='1000 * 1000'
obj.noise=0.0
```

[Go to Summary](#summary)
## `SampledSignal` (in `pydag\buffers\signals\SampledSignal.py`)

A class representing a sampled signal for continuously sampled data
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `sample_rate` | `float` | `1.0` | sample rate of the signal in Hz |


```python
# Example usage of `SampledSignal`
from pydag.buffers.signals.SampledSignal import SampledSignal  # Adjust import if needed

obj = SampledSignal()
obj.id="<string>"
obj.load_on_install=False
obj.sample_rate=1.0
```

[Go to Summary](#summary)
## `SampledSine` (in `pydag\buffers\signals\SampledSine.py`)

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
from pydag.buffers.signals.SampledSine import SampledSine  # Adjust import if needed

obj = SampledSine()
obj.sample_rate=1.0
obj.id="<string>"
obj.load_on_install=False
obj.f=1.0
obj.a=1.0
obj.p=0.0
obj.n=0.0
```

[Go to Summary](#summary)
## `Signal` (in `pydag\buffers\signals\Signal.py`)

Abstract base class for signals.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Signal`
from pydag.buffers.signals.Signal import Signal  # Adjust import if needed

obj = Signal()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `Sine` (in `pydag\buffers\signals\Sine.py`)

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
from pydag.buffers.signals.Sine import Sine  # Adjust import if needed

obj = Sine()
obj.id="<string>"
obj.load_on_install=False
obj.f=1.0
obj.a=1.0
obj.p=0.0
obj.n=0.0
```

[Go to Summary](#summary)
## `TimedSignal` (in `pydag\buffers\signals\TimedSignal.py`)

A signal that emits values at specified time intervals.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `times` | `list[float]` | `'list()'` | list of times in seconds when the signal should emit a value |
| `values` | `list[float]` | `'list()'` | list of values to emit at the specified times |


```python
# Example usage of `TimedSignal`
from pydag.buffers.signals.TimedSignal import TimedSignal  # Adjust import if needed

obj = TimedSignal()
obj.id="<string>"
obj.load_on_install=False
obj.times='list()'
obj.values='list()'
```

[Go to Summary](#summary)
## `ClippingTransformation` (in `pydag\buffers\transformations\ClippingTransformation.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `datatype` | `str` | `'DataType.FLOAT.value'` | type of data expected for the transform |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `lower_limit` | `float` | `0.0` | lower limit for clipping |
| `upper_limit` | `float` | `1.0` | upper limit for clipping |


```python
# Example usage of `ClippingTransformation`
from pydag.buffers.transformations.ClippingTransformation import ClippingTransformation  # Adjust import if needed

obj = ClippingTransformation()
obj.datatype='DataType.FLOAT.value'
obj.id="<string>"
obj.load_on_install=False
obj.lower_limit=0.0
obj.upper_limit=1.0
```

[Go to Summary](#summary)