# Adapter Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Adapter`](#adapter-from-Adapter) | Abstract base class for data adapters. |
| [`PublishAdapter`](#publishadapter-from-PublishAdapter) | abstract class for Adapter Interface for publishing to data sinks |
| [`ReadAdapter`](#readadapter-from-ReadAdapter) | abstract class for Adapter Interface for reading from data sources |
| [`SubscribeAdapter`](#subscribeadapter-from-SubscribeAdapter) | abstract class for Adapter Interface for subscribing from data sources |
| [`WriteAdapter`](#writeadapter-from-WriteAdapter) | abstract class for Adapter Interface for writing to data sinks |
| [`AdsAdapter`](#adsadapter-from-ads\AdsAdapter) |  |
| [`AudioAdapter`](#audioadapter-from-audio\AudioAdapter) |  |
| [`CsvReadAdapter`](#csvreadadapter-from-csv\CsvReadAdapter) |  |
| [`CsvWriteAdapter`](#csvwriteadapter-from-csv\CsvWriteAdapter) |  |
| [`HttpAdapter`](#httpadapter-from-http\HttpAdapter) | Adapter for reading and writing data from/to http endpoints |
| [`InfluxDbAdapter`](#influxdbadapter-from-influxdb\InfluxDbAdapter) | InfluxAdapter is a specialized adapter for reading from and writing to InfluxDB. |
| [`MQTTAdapter`](#mqttadapter-from-mqtt\MQTTAdapter) |  |
| [`OpcUaAdapter`](#opcuaadapter-from-opcua\OpcUaAdapter) |  |
| [`S7Adapter`](#s7adapter-from-s7\S7Adapter) | S7Adapter is a specialized adapter for reading from and writing to S7 PLCs. |
| [`ByteStreamAdapter`](#bytestreamadapter-from-socket\ByteStreamAdapter) |  |
| [`WebSocketAdapter`](#websocketadapter-from-socket\WebSocketAdapter) |  |
| [`SQLAdapter`](#sqladapter-from-sql\SQLAdapter) |  |



## `Adapter` (from `Adapter.py`)

Abstract base class for data adapters.
_No fields defined._

## `PublishAdapter` (from `PublishAdapter.py`)

abstract class for Adapter Interface for publishing to data sinks
    
_No fields defined._

## `ReadAdapter` (from `ReadAdapter.py`)

abstract class for Adapter Interface for reading from data sources
    
_No fields defined._

## `SubscribeAdapter` (from `SubscribeAdapter.py`)

abstract class for Adapter Interface for subscribing from data sources
    
_No fields defined._

## `WriteAdapter` (from `WriteAdapter.py`)

abstract class for Adapter Interface for writing to data sinks
    
_No fields defined._

## `AdsAdapter` (from `ads\AdsAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `ams_net_id` | `str` | `` | AMS Net Id to connect to for ADS Connection |
| `twincat` | `int` | `3` | Twincat version to use, e.g. 2 or 3 for TwinCAT 2/3 |


```python
# Example usage of `AdsAdapter`
from pydatagrabber import AdsAdapter  # Adjust import if needed

obj = AdsAdapter(
    ams_net_id="<string>",
    twincat=3
)
```

## `AudioAdapter` (from `audio\AudioAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sample_rate` | `int` | `44100` | sample rate of audio channel, usually 44100 Hz |
| `device` | `int` | `` | device number to use as input stream, if nothing is specified the default device is used |


```python
# Example usage of `AudioAdapter`
from pydatagrabber import AudioAdapter  # Adjust import if needed

obj = AudioAdapter(
    sample_rate=44100,
    device=1
)
```

## `CsvReadAdapter` (from `csv\CsvReadAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `file_path` | `str` | `` | path to the csv file to read |
| `all_at_once` | `bool` | `True` | read all data at once |
| `delimiter` | `str` | `';'` | delimiter to use to separate columns |
| `has_header` | `bool` | `True` | specifies whether a header is present in data |
| `auto_detect` | `bool` | `False` | specifies whether to use the csv sniffing option |
| `force_numeric` | `bool` | `True` | forces numeric parsing of data |


```python
# Example usage of `CsvReadAdapter`
from pydatagrabber import CsvReadAdapter  # Adjust import if needed

obj = CsvReadAdapter(
    file_path="path/to/file.txt",
    all_at_once=True,
    delimiter=';',
    has_header=True,
    auto_detect=False,
    force_numeric=True
)
```

## `CsvWriteAdapter` (from `csv\CsvWriteAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
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

obj = CsvWriteAdapter(
    folder="path/to/folder",
    file_post_fix="path/to/file.txt",
    file_extension='csv',
    with_timestamp=False,
    max_samples=1000000,
    delimiter=';',
    decimal_precision=3
)
```

## `HttpAdapter` (from `http\HttpAdapter.py`)

Adapter for reading and writing data from/to http endpoints
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `base_url` | `str` | `` | base URL for the HTTP requests, e.g. http://localhost:8080/api |
| `headers` | `dict[str]` | `` | headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'} |
| `json_path` | `bool` | `False` | if True, the response data is expected to be in JSON format and will be parsed accordingly to specification in address |


```python
# Example usage of `HttpAdapter`
from pydatagrabber import HttpAdapter  # Adjust import if needed

obj = HttpAdapter(
    base_url="https://example.com",
    headers="<string>",
    json_path=False
)
```

## `InfluxDbAdapter` (from `influxdb\InfluxDbAdapter.py`)

InfluxAdapter is a specialized adapter for reading from and writing to InfluxDB.
It inherits from ReadAdapter and WriteAdapter to provide both functionalities.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `endpoint` | `str` | `'http://localhost:8086'` | The endpoint URL for the InfluxDB instance. |
| `token` | `str` | `` | The authentication token for InfluxDB. |
| `org` | `str` | `'my-org'` | The organization name in InfluxDB. |


```python
# Example usage of `InfluxDbAdapter`
from pydatagrabber import InfluxDbAdapter  # Adjust import if needed

obj = InfluxDbAdapter(
    endpoint='http://localhost:8086',
    token="<string>",
    org='my-org'
)
```

## `MQTTAdapter` (from `mqtt\MQTTAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `endpoint` | `str` | `` | endpoint of the MQTT broker, e.g. test.mosquitto.org (public test broker) |
| `port` | `int` | `1883` | port of the mqtt broker |
| `keep_alive` | `int` | `60` | keep alive interval with broker |
| `force_numeric` | `bool` | `False` | specifies if the payload from mqtt topics should be parsed as numeric value, rather than string |
| `retain` | `bool` | `False` | specifies whether messages should be retained on publishing |
| `qos` | `int` | `0` | quality of service parameter of mqtt publish |


```python
# Example usage of `MQTTAdapter`
from pydatagrabber import MQTTAdapter  # Adjust import if needed

obj = MQTTAdapter(
    endpoint="<string>",
    port=1883,
    keep_alive=60,
    force_numeric=False,
    retain=False,
    qos=0
)
```

## `OpcUaAdapter` (from `opcua\OpcUaAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `endpoint` | `str` | `` | endpoint of the opc ua server, e.g. opc.tcp://localhost:48010 |


```python
# Example usage of `OpcUaAdapter`
from pydatagrabber import OpcUaAdapter  # Adjust import if needed

obj = OpcUaAdapter(
    endpoint="<string>"
)
```

## `S7Adapter` (from `s7\S7Adapter.py`)

S7Adapter is a specialized adapter for reading from and writing to S7 PLCs.
It inherits from ReadAdapter and WriteAdapter to provide both functionalities.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `host` | `str` | `'127.0.0.1'` | The IP address or hostname of the S7 PLC. |
| `rack` | `int` | `0` | The rack number of the S7 PLC. |
| `slot` | `int` | `1` | The slot number of the S7 PLC. |


```python
# Example usage of `S7Adapter`
from pydatagrabber import S7Adapter  # Adjust import if needed

obj = S7Adapter(
    host='127.0.0.1',
    rack=0,
    slot=1
)
```

## `ByteStreamAdapter` (from `socket\ByteStreamAdapter.py`)

_No fields defined._

## `WebSocketAdapter` (from `socket\WebSocketAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | `str` | `` | socket url, e.g. wss://localhost:10001 |


```python
# Example usage of `WebSocketAdapter`
from pydatagrabber import WebSocketAdapter  # Adjust import if needed

obj = WebSocketAdapter(
    url="https://example.com"
)
```

## `SQLAdapter` (from `sql\SQLAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `connection_str` | `str` | `` | connection string for the specific SQL database |


```python
# Example usage of `SQLAdapter`
from pydatagrabber import SQLAdapter  # Adjust import if needed

obj = SQLAdapter(
    connection_str="<string>"
)
```
