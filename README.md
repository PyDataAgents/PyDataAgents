# PyDataGrabber
is a IIoT python framework to generate autonomous Data Acquisition Agents for common industrial 
protocols, data sources and sinks.<br>
Examples:<br>
- OPCUA
- ADS
- TCP/IP, UDP and SERIAL
- MQTT
- INFLUXDB
![pydatagrabber_sources.png](docs/pydatagrabber_sources.png)
## architecture
the core element of the framework is a [(data)grabber](pydatagrabber/grabbers/Grabber.py)
a grabber can consists of one or more of the following [GrabberElements](pydatagrabber/grabbers/GrabberElement.py):
- adapters
- buffers
- mappings
- services

<br>each [GrabberElement](pydatagrabber/grabbers/GrabberElement.py) is dedicated for a special task within the datagrabber framework
<br>these tasks are highlighted below
### Grabber

### Adapter

### Buffer

### Service
