# PyDataGrabber
![pydatagrabber_sources.png](docs/pydatagrabber_logo.png)
<br>is a IIoT python framework to generate autonomous Data Acquisition Agents for common industrial 
protocols, data sources and sinks.<br>
Examples:<br>
- OPCUA
- ADS
- TCP/IP, UDP and SERIAL
- MQTT
- INFLUXDB
![pydatagrabber_sources_and_sinks.png](docs/pydatagrabber_sources_and_sinks.png)
## architecture
the core element of the framework is a [(data)grabber](pydatagrabber/grabbers/Grabber.py)
<br>a grabber can consists of one or more of the following [GrabberElements](pydatagrabber/grabbers/GrabberElement.py):
- adapters
- buffers
- mappings
- services
![pydatagrabber_framework.png](docs/pydatagrabber_framework.png)
<br>each [GrabberElement](pydatagrabber/grabbers/GrabberElement.py) is dedicated for a special task within the datagrabber framework
<br>these tasks are highlighted below
### Grabber
In order to create a `Grabber` application, you create a `Grabber` object with one or more of the elements described in the following sections.
The `Grabber` application follows a strict lifecycle, when being initialized and started.

### Buffer
an overview of all available buffers and their usage is given [here](docs/Buffers.md)
<br>A `Buffer` is the central element for data streaming and temporary storage inside a `Grabber` application.
<br>All `Buffer`s follow the FiFo-principle and are specified with a maximum `capacity` and datatypes (optional).
<br>Whenever data is transfered, it moves through a buffer.
<br>All `Buffer`'s adhere to the same interface:
```python
buffer = ListBuffer()
buffer.id = "BUF-1"
buffer.capacity = 10
buffer.datatype = "FLOAT"
buffer.description = "this is a float buffer"
buffer.unit = "mA"
buffer.initial_values = [0.02, 0.089]

buffer.push(elements) # push new elements to buffer

buffer.data(n=0, persistent=True) # get the buffers data, or n samples, with persistent True/False you specify whether to keep the elements n buffer the return type depends on the buffer implementation

buffer.size() # returns the size of the buffer --> int: number of samples
       
buffer.data_with_meta(n = 0, persistent = True): # returns the buffer data and all its meta data inside a defined json schema as dictionary

```

### Adapter
an overview of all available adapters and their usage is given [here](docs/Adapters.md)
<br>All `Adapter`'s adhere to the same composition of interfaces and their methods.
Every `Adapter` is initialized, installed, connected/disconnected and then depending on source or sink interaction: reads/subscribes from sources or writes/publishes to sinks.
<br>It is paramount, that `Adapter` methods are always used in the right order. Within a `Grabber` application, this is made sure by design, but when used outside, it must be taken care of by the developer.
<br>Here is an example workflow for the usage of an `Adapter`:
```python
adapter = CSVReadAdapter()
adapter.id = "CSV1",
adapter.file_path="path/to/file.txt",
adapter.delimiter=';',
adapter.has_header=True,
adapter.auto_detect=True,
adapter.force_numeric=True

adapter.install()

adapter.connect()

adapter.read_from_source()

adapter.disconnect()

adapter.deinstall()

```

### Mapping
an overview of all available mappings and their usage is given [here](docs/Mappings.md).
<br>In general a `Mapping` defines the interaction between an `Adapter` and one or more `Buffer`s in term of how often, how many samples and which data/information (`addresses`) in the source or sink are being accessed.
<br>The mapping defines this interaction and is used as data model to instantiate a background thread that runs for every specified `Mapping` and acquires or transfers the data from `Buffer`s to or from source or sinks. 
```python
m1 = Mapping()
m1.id = "M1"
m1.adapter_id = "MQTT1"
m1.addresses = ["signals/sine", "signals/linear"]
m1.buffer_ids = ["SINE1", "LINEAR1"]
m1.thread_type = ThreadType.MILLI_SECOND.value
m1.mapping_type = MappingType.WRITE.value
m1.sampling_period = 1000
m1.n = 0
m1.persistent = False
```

### Service
an overview of all available services and their usage is given [here](docs/Services.md)


## Installation and Usage
In order to install `pydatagrabber` use pip:
```python
pip install git+https://github.com/jhillenbrand/PyDataGrabber.git

# this will install the default branch, for a specific branch use

pip install git+https://github.com/jhillenbrand/PyDataGrabber.git@<branch>

# if the repo was installed already, use an uninstall before installing again

pip uninstall pydatagrabber -y; pip install git+https://github.com/jhillenbrand/PyDataGrabber.git
```

Project Dependencies can be found in [pyproject.toml](pyproject.toml)


## Examples and Testing
All Unittests and Examples are found in [tests](tests/)
