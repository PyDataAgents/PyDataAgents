# + Adapter Documentation

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

| Field | Type | Description |
|-------|------|-------------|
| `ams_net_id` | `str` | AMS Net Id to connect to for ADS Connection |
| `twincat` | `int` | Twincat version to use, e.g. 2 or 3 for TwinCAT 2/3 |

## `AudioAdapter` (from `audio\AudioAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `sample_rate` | `int` | sample rate of audio channel, usually 44100 Hz |
| `device` | `int` | device number to use as input stream, if nothing is specified the default device is used |

## `CsvReadAdapter` (from `csv\CsvReadAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | path to the csv file to read |
| `all_at_once` | `bool` | read all data at once |
| `delimiter` | `str` | delimiter to use to separate columns |
| `has_header` | `bool` | specifies whether a header is present in data |
| `auto_detect` | `bool` | specifies whether to use the csv sniffing option |
| `force_numeric` | `bool` | forces numeric parsing of data |

## `CsvWriteAdapter` (from `csv\CsvWriteAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `folder` | `str` | folder to save the csv files to |
| `file_post_fix` | `str` | postfix to use with every file |
| `file_extension` | `str` | extension of the files being created, specify without *.*, e.g. 'csv' or 'txt' |
| `with_timestamp` | `bool` | specify whether the current timestamp in UTC ms should be printed as column |
| `max_samples` | `int` | maximum number of samples in one file, if limit is reached a new file is being created |
| `delimiter` | `str` | delimiter to use for column separation |
| `decimal_precision` | `int` | maximum decimal precision of numeric values |

## `HttpAdapter` (from `http\HttpAdapter.py`)

Adapter for reading and writing data from/to http endpoints
    
| Field | Type | Description |
|-------|------|-------------|
| `base_url` | `str` | base URL for the HTTP requests, e.g. http://localhost:8080/api |
| `headers` | `dict[str]` | headers to be used in the HTTP requests, e.g. {'Content-Type': 'application/json', 'Authorization' : 'Bearer token'} |
| `json_path` | `bool` | if True, the response data is expected to be in JSON format and will be parsed accordingly to specification in address |

## `InfluxDbAdapter` (from `influxdb\InfluxDbAdapter.py`)

InfluxAdapter is a specialized adapter for reading from and writing to InfluxDB.
It inherits from ReadAdapter and WriteAdapter to provide both functionalities.
| Field | Type | Description |
|-------|------|-------------|
| `endpoint` | `str` | The endpoint URL for the InfluxDB instance. |
| `token` | `str` | The authentication token for InfluxDB. |
| `org` | `str` | The organization name in InfluxDB. |

## `MQTTAdapter` (from `mqtt\MQTTAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `endpoint` | `str` | endpoint of the MQTT broker, e.g. test.mosquitto.org (public test broker) |
| `port` | `int` | port of the mqtt broker |
| `keep_alive` | `int` | keep alive interval with broker |
| `force_numeric` | `bool` | specifies if the payload from mqtt topics should be parsed as numeric value, rather than string |
| `retain` | `bool` | specifies whether messages should be retained on publishing |
| `qos` | `int` | quality of service parameter of mqtt publish |

## `OpcUaAdapter` (from `opcua\OpcUaAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `endpoint` | `str` | endpoint of the opc ua server, e.g. opc.tcp://localhost:48010 |

## `S7Adapter` (from `s7\S7Adapter.py`)

S7Adapter is a specialized adapter for reading from and writing to S7 PLCs.
It inherits from ReadAdapter and WriteAdapter to provide both functionalities.
| Field | Type | Description |
|-------|------|-------------|
| `host` | `str` | The IP address or hostname of the S7 PLC. |
| `rack` | `int` | The rack number of the S7 PLC. |
| `slot` | `int` | The slot number of the S7 PLC. |

## `ByteStreamAdapter` (from `socket\ByteStreamAdapter.py`)

_No fields defined._

## `WebSocketAdapter` (from `socket\WebSocketAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `url` | `str` | socket url, e.g. wss://localhost:10001 |

## `SQLAdapter` (from `sql\SQLAdapter.py`)

| Field | Type | Description |
|-------|------|-------------|
| `connection_str` | `str` | connection string for the specific SQL database |
