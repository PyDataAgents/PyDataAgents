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

### Adapter
an overview of all available adapters and their usage is given [here](docs/Adapters.md)
All `Adapter`'s adhere to the same composition of interfaces and their methods.
Every `Adapter` is initialized, installed, connected/disconnected and then depending on source or sink interaction: reads/subscribes from sources or writes/publishes to sinks.
It is paramount, that `Adapter` methods are always used in the right order. Within a `Grabber` application, this is made sure by design, but when used outside, it must be taken care of by the developer.
Here is an example workflow for the usage of an `Adapter`:
```python

```

### Buffer
an overview of all available buffers and their usage is given [here](docs/Buffers.md)

### Mapping
an overview of all available mappings and their usage is given [here](docs/Mappings.md)

### Service
an overview of all available services and their usage is given [here](docs/Services.md)
