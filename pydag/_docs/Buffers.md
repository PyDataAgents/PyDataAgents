# Buffers Documentation

## Summary

| Class | Description | Icon |
|-------|-------------|------|
| [`Buffer`](#buffer-in-pydagbuffersbufferpy) | Abstract base class for buffers. | ![Buffer](element_icons/Buffer.png)
| [`DatasetBuffer`](#datasetbuffer-in-pydagbuffersdatasetbufferpy) | A `Buffer` that loads a dataset and stores it in its elements     | ![DatasetBuffer](element_icons/DatasetBuffer.png)
| [`DictBuffer`](#dictbuffer-in-pydagbuffersdictbufferpy) | Buffer that stores its values in a dictionary column-wise (each key -> list). | ![DictBuffer](element_icons/DictBuffer.png)
| [`ListBuffer`](#listbuffer-in-pydagbufferslistbufferpy) | `Buffer` that stores its values in a capacity limited list     | ![ListBuffer](element_icons/ListBuffer.png)
| [`ObjectTransformation`](#objecttransformation-in-pydagbuffersobjecttransformationpy) | Abstract base class for object transformations for buffers | ![ObjectTransformation](element_icons/ObjectTransformation.png)
| [`ObservedListBuffer`](#observedlistbuffer-in-pydagbuffersobservedlistbufferpy) |  | ![ObservedListBuffer](element_icons/ObservedListBuffer.png)
| [`SampledBuffer`](#sampledbuffer-in-pydagbufferssampledbufferpy) | `Buffer` that samples a `signal` at a specified interval for `n`samples at a time. | ![SampledBuffer](element_icons/SampledBuffer.png)
| [`SignalBuffer`](#signalbuffer-in-pydagbufferssignalbufferpy) | `Buffer` that holds signals with a specific start time and elapsed time and is defined by the referenced `signal`'s values.     | ![SignalBuffer](element_icons/SignalBuffer.png)
| [`TimedBuffer`](#timedbuffer-in-pydagbufferstimedbufferpy) | A buffer that stores data with timestamps.Inherits from `ListBuffer`. | ![TimedBuffer](element_icons/TimedBuffer.png)
| [`TransformsBuffer`](#transformsbuffer-in-pydagbufferstransformsbufferpy) | TransformsBuffer is a subclass of ListBuffer that allows for data transformation.It is used to transform data from one format to another. | ![TransformsBuffer](element_icons/TransformsBuffer.png)
| [`GeometryBuffer`](#geometrybuffer-in-pydagbuffersgeometrygeometrybufferpy) |  | ![GeometryBuffer](element_icons/GeometryBuffer.png)
| [`LinearTrend`](#lineartrend-in-pydagbufferssignalslineartrendpy) | A signal that simulates a linear trend | ![LinearTrend](element_icons/LinearTrend.png)
| [`SampledSignal`](#sampledsignal-in-pydagbufferssignalssampledsignalpy) | A class representing a sampled signal for continuously sampled data | ![SampledSignal](element_icons/SampledSignal.png)
| [`SampledSine`](#sampledsine-in-pydagbufferssignalssampledsinepy) | A class to represent a sampled sine wave signal.Attributes:    f (float): The frequency of the sine wave in Hz.    a (float): The amplitude of the sine wave.    sample_rate (int): The number of samples per second.    p (float): The phase of the sine wave in °. | ![SampledSine](element_icons/SampledSine.png)
| [`Sawtooth`](#sawtooth-in-pydagbufferssignalssawtoothpy) | A class to represent a sawtooth wave signal. | ![Sawtooth](element_icons/Sawtooth.png)
| [`Signal`](#signal-in-pydagbufferssignalssignalpy) | Abstract base class for signals. | ![Signal](element_icons/Signal.png)
| [`Sine`](#sine-in-pydagbufferssignalssinepy) | A class to represent a sine wave signal. | ![Sine](element_icons/Sine.png)
| [`TimedSignal`](#timedsignal-in-pydagbufferssignalstimedsignalpy) | A signal that emits values at specified time intervals. | ![TimedSignal](element_icons/TimedSignal.png)
| [`ClippingTransformation`](#clippingtransformation-in-pydagbufferstransformationsclippingtransformationpy) |  | ![ClippingTransformation](element_icons/ClippingTransformation.png)



## `Buffer` (in `pydag\buffers\Buffer.py`)

Abstract base class for buffers.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `capacity` | `int` | `'AgentConfig.INFINITE_CAPACITY'` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `duplicate_ids` | `list` | `'list()'` | id's of the other buffers used for duplicating the data |


```python
# Example usage of `Buffer`
from pydag.buffers.Buffer import Buffer  # Adjust import if needed

obj = Buffer()
obj.id="<string>"
obj.load_on_install=False
obj.capacity='AgentConfig.INFINITE_CAPACITY'
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.duplicate_ids='list()'
```

[Go to Summary](#summary)
## `DatasetBuffer` (in `pydag\buffers\DatasetBuffer.py`)

A `Buffer` that loads a dataset and stores it in its elements
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `'AgentConfig.INFINITE_CAPACITY'` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `duplicate_ids` | `list` | `'list()'` | id's of the other buffers used for duplicating the data |
| `timestamps_enabled` | `bool` | `False` | Whether timestamps are enabled for this buffer. If the parent buffer has a timestamps column which is named in the same way as this buffer's timestamps_key, those timestamps will be copied over. If set to False and a timestamp column is present in the input data, it will be ignored. |
| `timestamps_key` | `str` | `'timestamps'` | Key under which timestamps are exposed. |
| `index_enabled` | `bool` | `False` | Whether an index column is enabled for this buffer. The index column is a simple integer sequence starting from 0 and adds +1 per point. If the parent buffer has an index column which is named in the same way as this buffer's index_key, those indices will be copied over. If set to False and an index column is present in the input data, it will be ignored. |
| `index_key` | `str` | `'index'` | Key name for index column. |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `dataset_name` | `str` | `'DatasetNames.Blobs.value'` | Dataset names. Tested are:
                                                                                ArrowHead: https://www.timeseriesclassification.com/description.php?Dataset=ArrowHead,
                                                                                AbnormalHeartbeat: https://www.timeseriesclassification.com/description.php?Dataset=AbnormalHeartbeat,
                                                                                Car: https://www.timeseriesclassification.com/description.php?Dataset=Car,
                                                                                ChlorineConcentration: https://www.timeseriesclassification.com/description.php?Dataset=ChlorineConcentration,
                                                                                Crop: https://www.timeseriesclassification.com/description.php?Dataset=Crop,
                                                                                ECG5000: https://www.timeseriesclassification.com/description.php?Dataset=ECG5000,
                                                                                ElectricDevices: https://www.timeseriesclassification.com/description.php?Dataset=ElectricDevices,
                                                                                FordA: https://www.timeseriesclassification.com/description.php?Dataset=FordA,
                                                                                InsectSound: https://www.timeseriesclassification.com/description.php?Dataset=InsectSound,
                                                                                KeplerLightCurves: https://www.timeseriesclassification.com/description.php?Dataset=KeplerLightCurves,
                                                                                Plane: https://www.timeseriesclassification.com/description.php?Dataset=Plane,
                                                                                ShapesAll: https://www.timeseriesclassification.com/description.php?Dataset=ShapesAll,
                                                                                UWaveGestureLibrary:https://www.timeseriesclassification.com/description.php?Dataset=UWaveGestureLibrary,
                                                                                Wafer: https://www.timeseriesclassification.com/description.php?Dataset=Wafer,
                                                                                Wine: https://www.timeseriesclassification.com/description.php?Dataset=Wine,
                                                                                Blobs: This is a sklearn dataset which creates Clusters. https://scikit-learn.org/stable/modules/generated/sklearn.datasets.make_blobs.html 
                                                                                CNC: This is a dataset from a publication which contains vibration measuremens from a CNC machine. The dataset is available at: https://archive.ics.uci.edu/dataset/752/bosch+cnc+machining+dataset and https://github.com/boschresearch/CNC_Machining. As mentioned on https://github.com/boschresearch/CNC_Machining please cite the following paper if you use the dataset: Tnani, Mohamed-Ali; Feil, Michael; Diepold, Klaus. Smart Data Collection System for Brownfield CNC Milling Machines: A New Benchmark Dataset for Data-Driven Machine Monitoring. Procedia CIRP2022,107, 131–136. Only datasets with "DE", "FE" and "BA" data is used.
                                                                                CWRU: The dataset is available at: https://github.com/srigas/CWRU_Bearing_NumPy and originally from https://engineering.case.edu/bearingdatacenter to where you should refer if you use the dataset.      
                                                                                You can test other datasets from https://www.timeseriesclassification.com/dataset.php as well but they are not tested yet. |
| `sort_by_y` | `bool` | `False` | whether to sort the data by the labels y. |


```python
# Example usage of `DatasetBuffer`
from pydag.buffers.DatasetBuffer import DatasetBuffer  # Adjust import if needed

obj = DatasetBuffer()
obj.capacity='AgentConfig.INFINITE_CAPACITY'
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.duplicate_ids='list()'
obj.timestamps_enabled=False
obj.timestamps_key='timestamps'
obj.index_enabled=False
obj.index_key='index'
obj.id="<string>"
obj.load_on_install=False
obj.dataset_name='DatasetNames.Blobs.value'
obj.sort_by_y=False
```

[Go to Summary](#summary)
## `DictBuffer` (in `pydag\buffers\DictBuffer.py`)

Buffer that stores its values in a dictionary column-wise (each key -> list).
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `'AgentConfig.INFINITE_CAPACITY'` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `duplicate_ids` | `list` | `'list()'` | id's of the other buffers used for duplicating the data |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `timestamps_enabled` | `bool` | `False` | Whether timestamps are enabled for this buffer. If the parent buffer has a timestamps column which is named in the same way as this buffer's timestamps_key, those timestamps will be copied over. If set to False and a timestamp column is present in the input data, it will be ignored. |
| `timestamps_key` | `str` | `'timestamps'` | Key under which timestamps are exposed. |
| `index_enabled` | `bool` | `False` | Whether an index column is enabled for this buffer. The index column is a simple integer sequence starting from 0 and adds +1 per point. If the parent buffer has an index column which is named in the same way as this buffer's index_key, those indices will be copied over. If set to False and an index column is present in the input data, it will be ignored. |
| `index_key` | `str` | `'index'` | Key name for index column. |


```python
# Example usage of `DictBuffer`
from pydag.buffers.DictBuffer import DictBuffer  # Adjust import if needed

obj = DictBuffer()
obj.capacity='AgentConfig.INFINITE_CAPACITY'
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.duplicate_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.timestamps_enabled=False
obj.timestamps_key='timestamps'
obj.index_enabled=False
obj.index_key='index'
```

[Go to Summary](#summary)
## `ListBuffer` (in `pydag\buffers\ListBuffer.py`)

`Buffer` that stores its values in a capacity limited list
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `'AgentConfig.INFINITE_CAPACITY'` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `duplicate_ids` | `list` | `'list()'` | id's of the other buffers used for duplicating the data |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `ListBuffer`
from pydag.buffers.ListBuffer import ListBuffer  # Adjust import if needed

obj = ListBuffer()
obj.capacity='AgentConfig.INFINITE_CAPACITY'
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.duplicate_ids='list()'
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
## `ObservedListBuffer` (in `pydag\buffers\ObservedListBuffer.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `'AgentConfig.INFINITE_CAPACITY'` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `duplicate_ids` | `list` | `'list()'` | id's of the other buffers used for duplicating the data |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `input_observers` | `list[BufferObserver]` | `'list()'` | list of observers that observe new input to the buffer inside the push method |
| `output_observers` | `list[BufferObserver]` | `'list()'` | list of observers that observe output of the buffer inside the data method |


```python
# Example usage of `ObservedListBuffer`
from pydag.buffers.ObservedListBuffer import ObservedListBuffer  # Adjust import if needed

obj = ObservedListBuffer()
obj.capacity='AgentConfig.INFINITE_CAPACITY'
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.duplicate_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.input_observers='list()'
obj.output_observers='list()'
```

[Go to Summary](#summary)
## `SampledBuffer` (in `pydag\buffers\SampledBuffer.py`)

`Buffer` that samples a `signal` at a specified interval for `n`samples at a time.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `'AgentConfig.INFINITE_CAPACITY'` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `duplicate_ids` | `list` | `'list()'` | id's of the other buffers used for duplicating the data |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `signal` | `SampledSignal` | `` | a signal object to simulate data |
| `sampling_period` | `int` | `100` | interval in milliseconds for update |
| `n` | `int` | `1` | number of samples to create at once |


```python
# Example usage of `SampledBuffer`
from pydag.buffers.SampledBuffer import SampledBuffer  # Adjust import if needed

obj = SampledBuffer()
obj.capacity='AgentConfig.INFINITE_CAPACITY'
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.duplicate_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.signal="<value>"
obj.sampling_period=100
obj.n=1
```

[Go to Summary](#summary)
## `SignalBuffer` (in `pydag\buffers\SignalBuffer.py`)

`Buffer` that holds signals with a specific start time and elapsed time and is defined by the referenced `signal`'s values.    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `'AgentConfig.INFINITE_CAPACITY'` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `duplicate_ids` | `list` | `'list()'` | id's of the other buffers used for duplicating the data |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `signal` | `Signal` | `` | a signal object to simulate data |
| `sampling_period` | `int` | `100` | interval in milliseconds for update |


```python
# Example usage of `SignalBuffer`
from pydag.buffers.SignalBuffer import SignalBuffer  # Adjust import if needed

obj = SignalBuffer()
obj.capacity='AgentConfig.INFINITE_CAPACITY'
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.duplicate_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.signal="<value>"
obj.sampling_period=100
```

[Go to Summary](#summary)
## `TimedBuffer` (in `pydag\buffers\TimedBuffer.py`)

A buffer that stores data with timestamps.
Inherits from `ListBuffer`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `'AgentConfig.INFINITE_CAPACITY'` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `duplicate_ids` | `list` | `'list()'` | id's of the other buffers used for duplicating the data |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `TimedBuffer`
from pydag.buffers.TimedBuffer import TimedBuffer  # Adjust import if needed

obj = TimedBuffer()
obj.capacity='AgentConfig.INFINITE_CAPACITY'
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.duplicate_ids='list()'
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `TransformsBuffer` (in `pydag\buffers\TransformsBuffer.py`)

TransformsBuffer is a subclass of ListBuffer that allows for data transformation.
It is used to transform data from one format to another.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `'AgentConfig.INFINITE_CAPACITY'` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `duplicate_ids` | `list` | `'list()'` | id's of the other buffers used for duplicating the data |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `transformations` | `list[ObjectTransformation]` | `[]` | List of transformations to apply to the data |


```python
# Example usage of `TransformsBuffer`
from pydag.buffers.TransformsBuffer import TransformsBuffer  # Adjust import if needed

obj = TransformsBuffer()
obj.capacity='AgentConfig.INFINITE_CAPACITY'
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.duplicate_ids='list()'
obj.id="<string>"
obj.load_on_install=False
obj.transformations=[]
```

[Go to Summary](#summary)
## `GeometryBuffer` (in `pydag\buffers\geometry\GeometryBuffer.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capacity` | `int` | `'AgentConfig.INFINITE_CAPACITY'` | Number of elements that can be stored in buffer before being discarded in FiFo fashion. If set to -1, then there is no capacity for this buffer. |
| `data_type` | `str` | `'DataType.FLOAT.value'` | datatype to expect from buffer elements, can be DataType enum or list of enums |
| `initial_values` | `any` | `` | initial values in buffer |
| `unit` | `any` | `` | unit of element values in this buffer, can be string or list of strings |
| `description` | `str` | `` | buffer description |
| `duplicate_ids` | `list` | `'list()'` | id's of the other buffers used for duplicating the data |
| `timestamps_enabled` | `bool` | `False` | Whether timestamps are enabled for this buffer. If the parent buffer has a timestamps column which is named in the same way as this buffer's timestamps_key, those timestamps will be copied over. If set to False and a timestamp column is present in the input data, it will be ignored. |
| `timestamps_key` | `str` | `'timestamps'` | Key under which timestamps are exposed. |
| `index_enabled` | `bool` | `False` | Whether an index column is enabled for this buffer. The index column is a simple integer sequence starting from 0 and adds +1 per point. If the parent buffer has an index column which is named in the same way as this buffer's index_key, those indices will be copied over. If set to False and an index column is present in the input data, it will be ignored. |
| `index_key` | `str` | `'index'` | Key name for index column. |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `resolution` | `list[int]` | `'list()'` |  |


```python
# Example usage of `GeometryBuffer`
from pydag.buffers.geometry.GeometryBuffer import GeometryBuffer  # Adjust import if needed

obj = GeometryBuffer()
obj.capacity='AgentConfig.INFINITE_CAPACITY'
obj.data_type='DataType.FLOAT.value'
obj.initial_values="<value>"
obj.unit="<value>"
obj.description="<string>"
obj.duplicate_ids='list()'
obj.timestamps_enabled=False
obj.timestamps_key='timestamps'
obj.index_enabled=False
obj.index_key='index'
obj.id="<string>"
obj.load_on_install=False
obj.resolution='list()'
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
## `Sawtooth` (in `pydag\buffers\signals\Sawtooth.py`)

A class to represent a sawtooth wave signal.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `f` | `float` | `1.0` | frequency of sawtooth wave in Hz |
| `a` | `float` | `1.0` | amplitude of sawtooth wave |


```python
# Example usage of `Sawtooth`
from pydag.buffers.signals.Sawtooth import Sawtooth  # Adjust import if needed

obj = Sawtooth()
obj.id="<string>"
obj.load_on_install=False
obj.f=1.0
obj.a=1.0
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