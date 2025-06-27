# Adapters Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Adapter`](#adapter-from-Adapter) | Abstract base class for `Adapters`. All `Adapters` must inherit from this class. |
| [`PublishAdapter`](#publishadapter-from-PublishAdapter) | abstract class for `Adapter` Interface for publishing to data sinks.<br>new `Adapters` that allow for publishing to a sink via callback must inherit this class next to `Adapter`. |
| [`ReadAdapter`](#readadapter-from-ReadAdapter) | abstract class for `Adapter` Interface for reading from data sources.<br>new `Adapters` that allow for reading from a source via one-shot polling must inherit this class next to `Adapter`. |
| [`SubscribeAdapter`](#subscribeadapter-from-SubscribeAdapter) | abstract class for `Adapter` Interface for subscribing from data sources<br>new `Adapters` that allow for subscribing to a source via callback must inherit this class next to `Adapter`. |
| [`WriteAdapter`](#writeadapter-from-WriteAdapter) | abstract class for Adapter Interface for writing to data sinks<br>new `Adapters` that allow for writing to a sink via one-shot polling must inherit this class next to `Adapter`. |
| [`AdsAdapter`](#adsadapter-from-ads\AdsAdapter) | `Adapter` for reading and writing data from/to Beckhoff TwinCAT PLCs via ADS (Automation Device Specification).     |
| [`AudioAdapter`](#audioadapter-from-audio\AudioAdapter) | `Adapter` for subscribing to a system's audio input channels (e.g. from a USB microphone) using the `sounddevice` library.     |
| [`CsvReadAdapter`](#csvreadadapter-from-csv\CsvReadAdapter) | `Adapter` for reading data from CSV files.     |
| [`CsvWriteAdapter`](#csvwriteadapter-from-csv\CsvWriteAdapter) | `Adapter` for writing data to CSV files.     |
| [`HttpAdapter`](#httpadapter-from-http\HttpAdapter) | `Adapter` for reading and writing data from/to http endpoints     |
| [`InfluxDbAdapter`](#influxdbadapter-from-influxdb\InfluxDbAdapter) | `Adapter` thats reads or writes to InfluxDB.     |
| [`MQTTAdapter`](#mqttadapter-from-mqtt\MQTTAdapter) | `Adapter` for subscribing or writing data from/to MQTT topics.     |
| [`OpcUaAdapter`](#opcuaadapter-from-opcua\OpcUaAdapter) | `Adapter` for reading and writing data from/to OPC UA servers.     |
| [`S7Adapter`](#s7adapter-from-s7\S7Adapter) | `Adapter`reading from and writing to S7 PLCs.     |
| [`ByteStreamAdapter`](#bytestreamadapter-from-socket\ByteStreamAdapter) |  |
| [`WebSocketAdapter`](#websocketadapter-from-socket\WebSocketAdapter) | `Adapter` for subscribing and writing data from/to WebSocket endpoints.     |
| [`SQLAdapter`](#sqladapter-from-sql\SQLAdapter) | `Adapter` for reading and writing data from/to SQL databases using pyodbc.<br>Required ODBC driver must be installed for the specific SQL database (e.g. MySQL, PostgreSQL, SQLite, etc.) and sytem |



## `Adapter` (from `Adapter.py`)

Abstract base class for `Adapters`. All `Adapters` must inherit from this class.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Adapter`
from pydatagrabber import Adapter  # Adjust import if needed

obj = Adapter()
obj.id="<string>"
obj.load_on_install=False
```

## `PublishAdapter` (from `PublishAdapter.py`)

abstract class for `Adapter` Interface for publishing to data sinks.
<br>new `Adapters` that allow for publishing to a sink via callback must inherit this class next to `Adapter`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `PublishAdapter`
from pydatagrabber import PublishAdapter  # Adjust import if needed

obj = PublishAdapter()
obj.id="<string>"
obj.load_on_install=False
```

## `ReadAdapter` (from `ReadAdapter.py`)

abstract class for `Adapter` Interface for reading from data sources.
<br>new `Adapters` that allow for reading from a source via one-shot polling must inherit this class next to `Adapter`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `ReadAdapter`
from pydatagrabber import ReadAdapter  # Adjust import if needed

obj = ReadAdapter()
obj.id="<string>"
obj.load_on_install=False
```

## `SubscribeAdapter` (from `SubscribeAdapter.py`)

abstract class for `Adapter` Interface for subscribing from data sources
<br>new `Adapters` that allow for subscribing to a source via callback must inherit this class next to `Adapter`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `SubscribeAdapter`
from pydatagrabber import SubscribeAdapter  # Adjust import if needed

obj = SubscribeAdapter()
obj.id="<string>"
obj.load_on_install=False
```

## `WriteAdapter` (from `WriteAdapter.py`)

abstract class for Adapter Interface for writing to data sinks
<br>new `Adapters` that allow for writing to a sink via one-shot polling must inherit this class next to `Adapter`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `WriteAdapter`
from pydatagrabber import WriteAdapter  # Adjust import if needed

obj = WriteAdapter()
obj.id="<string>"
obj.load_on_install=False
```

## `AdsAdapter` (from `ads\AdsAdapter.py`)

`Adapter` for reading and writing data from/to Beckhoff TwinCAT PLCs via ADS (Automation Device Specification).
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `ams_net_id` | `str` | `` | AMS Net Id to connect to for ADS Connection |
| `twincat` | `int` | `3` | Twincat version to use, e.g. 2 or 3 for TwinCAT 2/3 |


```python
# Example usage of `AdsAdapter`
from pydatagrabber import AdsAdapter  # Adjust import if needed

obj = AdsAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.ams_net_id="<string>"
obj.twincat=3
```

## `AudioAdapter` (from `audio\AudioAdapter.py`)

`Adapter` for subscribing to a system's audio input channels (e.g. from a USB microphone) using the `sounddevice` library.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `sample_rate` | `int` | `44100` | sample rate of audio channel, usually 44100 Hz |
| `device` | `int` | `` | device number to use as input stream, if nothing is specified the default device is used |


```python
# Example usage of `AudioAdapter`
from pydatagrabber import AudioAdapter  # Adjust import if needed

obj = AudioAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.sample_rate=44100
obj.device=1
```

## `CsvReadAdapter` (from `csv\CsvReadAdapter.py`)

`Adapter` for reading data from CSV files.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `file_path` | `str` | `` | path to the csv file to read |
| `all_at_once` | `bool` | `True` | read all data at once |
| `delimiter` | `str` | `';'` | delimiter to use to separate columns |
| `has_header` | `bool` | `True` | specifies whether a header is present in data |
| `auto_detect` | `bool` | `False` | specifies whether to use the csv sniffing option |
| `force_numeric` | `bool` | `True` | forces numeric parsing of data |


```python
# Example usage of `CsvReadAdapter`
from pydatagrabber import CsvReadAdapter  # Adjust import if needed

obj = CsvReadAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.file_path="path/to/file.txt"
obj.all_at_once=True
obj.delimiter=';'
obj.has_header=True
obj.auto_detect=False
obj.force_numeric=True
```

## `CsvWriteAdapter` (from `csv\CsvWriteAdapter.py`)

`Adapter` for writing data to CSV files.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `folder` | `str` | `` | folder to save the csv files to |
| `file_post_fix` | `str` | `` | postfix to use with every file |
| `file_extension` | `str` | `'csv'` | extension of the files being created, specify without *.*, e.g. 'csv' or 'txt' |
| `with_timestamp` | `bool` | `False` | specify whether the current timestamp in UTC ms should be printed as column |
| `max_samples` | `int` | `1000000` | maximum number of samples in one file, if limit is reached a new file is being created |
| `delimiter` | `str` | `';'` | delimiter to use for column separation |
| `decimal_precision` | `int` | `3` | maximum decimal precision of numeric values |


```python
# Example usage of `CsvWriteAdapter`
from pydatagrabber import CsvWriteAdapter  # Adjust import if needed

obj = CsvWriteAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.folder="path/to/folder"
obj.file_post_fix="path/to/file.txt"
obj.file_extension='csv'
obj.with_timestamp=False
obj.max_samples=1000000
obj.delimiter=';'
obj.decimal_precision=3
```

## `HttpAdapter` (from `http\HttpAdapter.py`)

`Adapter` for reading and writing data from/to http endpoints
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `base_url` | `str` | `` | base URL for the HTTP requests, e.g. http://localhost:8080/api |
| `headers` | `dict[str]` | `` | headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'} |
| `json_path` | `bool` | `False` | if True, the response data is expected to be in JSON format and will be parsed accordingly to specification in address |


```python
# Example usage of `HttpAdapter`
from pydatagrabber import HttpAdapter  # Adjust import if needed

obj = HttpAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.base_url="https://example.com"
obj.headers="<string>"
obj.json_path=False
```

## `InfluxDbAdapter` (from `influxdb\InfluxDbAdapter.py`)

`Adapter` thats reads or writes to InfluxDB.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `endpoint` | `str` | `'http://localhost:8086'` | The endpoint URL for the InfluxDB instance. |
| `token` | `str` | `` | The authentication token for InfluxDB. |
| `org` | `str` | `'my-org'` | The organization name in InfluxDB. |


```python
# Example usage of `InfluxDbAdapter`
from pydatagrabber import InfluxDbAdapter  # Adjust import if needed

obj = InfluxDbAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.endpoint='http://localhost:8086'
obj.token="<string>"
obj.org='my-org'
```

## `MQTTAdapter` (from `mqtt\MQTTAdapter.py`)

`Adapter` for subscribing or writing data from/to MQTT topics.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `endpoint` | `str` | `` | endpoint of the MQTT broker, e.g. test.mosquitto.org (public test broker) |
| `port` | `int` | `1883` | port of the mqtt broker |
| `keep_alive` | `int` | `60` | keep alive interval with broker |
| `force_numeric` | `bool` | `False` | specifies if the payload from mqtt topics should be parsed as numeric value, rather than string |
| `retain` | `bool` | `False` | specifies whether messages should be retained on publishing |
| `qos` | `int` | `0` | quality of service parameter of mqtt publish |


```python
# Example usage of `MQTTAdapter`
from pydatagrabber import MQTTAdapter  # Adjust import if needed

obj = MQTTAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.endpoint="<string>"
obj.port=1883
obj.keep_alive=60
obj.force_numeric=False
obj.retain=False
obj.qos=0
```

## `OpcUaAdapter` (from `opcua\OpcUaAdapter.py`)

`Adapter` for reading and writing data from/to OPC UA servers.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `endpoint` | `str` | `` | endpoint of the opc ua server, e.g. opc.tcp://localhost:48010 |


```python
# Example usage of `OpcUaAdapter`
from pydatagrabber import OpcUaAdapter  # Adjust import if needed

obj = OpcUaAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.endpoint="<string>"
```

## `S7Adapter` (from `s7\S7Adapter.py`)

`Adapter`reading from and writing to S7 PLCs.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `host` | `str` | `'127.0.0.1'` | The IP address or hostname of the S7 PLC. |
| `rack` | `int` | `0` | The rack number of the S7 PLC. |
| `slot` | `int` | `1` | The slot number of the S7 PLC. |


```python
# Example usage of `S7Adapter`
from pydatagrabber import S7Adapter  # Adjust import if needed

obj = S7Adapter()
obj.id="<string>"
obj.load_on_install=False
obj.host='127.0.0.1'
obj.rack=0
obj.slot=1
```

## `ByteStreamAdapter` (from `socket\ByteStreamAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `ByteStreamAdapter`
from pydatagrabber import ByteStreamAdapter  # Adjust import if needed

obj = ByteStreamAdapter()
obj.id="<string>"
obj.load_on_install=False
```

## `WebSocketAdapter` (from `socket\WebSocketAdapter.py`)

`Adapter` for subscribing and writing data from/to WebSocket endpoints.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `url` | `str` | `` | socket url, e.g. wss://localhost:10001 |


```python
# Example usage of `WebSocketAdapter`
from pydatagrabber import WebSocketAdapter  # Adjust import if needed

obj = WebSocketAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.url="https://example.com"
```

## `SQLAdapter` (from `sql\SQLAdapter.py`)

`Adapter` for reading and writing data from/to SQL databases using pyodbc.
<br>Required ODBC driver must be installed for the specific SQL database (e.g. MySQL, PostgreSQL, SQLite, etc.) and sytem
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `connection_str` | `str` | `` | connection string for the specific SQL database |


```python
# Example usage of `SQLAdapter`
from pydatagrabber import SQLAdapter  # Adjust import if needed

obj = SQLAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.connection_str="<string>"
```
