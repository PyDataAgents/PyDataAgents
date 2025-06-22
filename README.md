# PyDataGrabber
![pydatagrabber_sources.png](docs/pydatagrabber_logo.png)
is a IIoT python framework to generate autonomous Data Acquisition Agents for common industrial 
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
a grabber can consists of one or more of the following [GrabberElements](pydatagrabber/grabbers/GrabberElement.py):
- adapters
- buffers
- mappings
- services
![pydatagrabber_framework.png](docs/pydatagrabber_framework.png)
<br>each [GrabberElement](pydatagrabber/grabbers/GrabberElement.py) is dedicated for a special task within the datagrabber framework
<br>these tasks are highlighted below
### Grabber

### Adapter
an overview of all available adapters and their usage is given [here](docs/Adapters.md)

### Buffer
an overview of all available buffers and their usage is given [here](docs/Buffers.md)

### Mapping
an overview of all available mappings and their usage is given [here](docs/Mappings.md)

### Service
an overview of all available services and their usage is given [here](docs/Services.md)
