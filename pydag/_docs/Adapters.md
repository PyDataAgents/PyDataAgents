# Adapters Documentation

## Summary

| Class | Description |
|-------|-------------|
| [`Adapter`](#adapter-in-pydagadaptersadapterpy) | Abstract base class for `Adapters`. All `Adapters` must inherit from this class. |
| [`PublishAdapter`](#publishadapter-in-pydagadapterspublishadapterpy) | abstract class for `Adapter` Interface for publishing to data sinks.<br>new `Adapters` that allow for publishing to a sink via callback must inherit this class next to `Adapter`. |
| [`ReadAdapter`](#readadapter-in-pydagadaptersreadadapterpy) | abstract class for `Adapter` Interface for reading from data sources.<br>new `Adapters` that allow for reading from a source via one-shot polling must inherit this class next to `Adapter`. |
| [`SubscribeAdapter`](#subscribeadapter-in-pydagadapterssubscribeadapterpy) | abstract class for `Adapter` Interface for subscribing from data sources<br>new `Adapters` that allow for subscribing to a source via callback must inherit this class next to `Adapter`. |
| [`WriteAdapter`](#writeadapter-in-pydagadapterswriteadapterpy) | abstract class for Adapter Interface for writing to data sinks<br>new `Adapters` that allow for writing to a sink via one-shot polling must inherit this class next to `Adapter`. |
| [`AdsAdapter`](#adsadapter-in-pydagadaptersadsadsadapterpy) | `Adapter` for reading and writing data from/to Beckhoff TwinCAT PLCs via ADS (Automation Device Specification).     |
| [`AudioAdapter`](#audioadapter-in-pydagadaptersaudioaudioadapterpy) | `Adapter` for subscribing to a system's audio input channels (e.g. from a USB microphone) using the `sounddevice` library.     |
| [`SolidPDMAdapter`](#solidpdmadapter-in-pydagadapterscadsolidpdmadapterpy) |  |
| [`CsvReadAdapter`](#csvreadadapter-in-pydagadapterscsvcsvreadadapterpy) | `Adapter` for reading data from CSV files.     |
| [`CsvWriteAdapter`](#csvwriteadapter-in-pydagadapterscsvcsvwriteadapterpy) | `Adapter` for writing data to CSV files.     |
| [`InfluxDbAdapter`](#influxdbadapter-in-pydagadaptersdbinfluxdbadapterpy) | `Adapter` thats reads or writes to InfluxDB.<br>Address Schema:<br>address = "b=[bucket];m=[measurement];f=[field]" |
| [`SQLAdapter`](#sqladapter-in-pydagadaptersdbsqladapterpy) | `Adapter` for reading and writing data from/to SQL databases using pyodbc.<br>Required ODBC driver must be installed for the specific SQL database (e.g. MySQL, PostgreSQL, SQLite, etc.) and system<br><br>The `addresses` in `_on_write` and `_on_read` is used to specify the SQL statement to execute. SQL statements should adhere the following format:- SELECT: 'SELECT [column1], [column2], ... FROM [table] WHERE [column3] = [value1]'- CREATE TABLE: 'CREATE TABLE ...'        - INSERT: 'INSERT INTO [table] ([column1], [column2], [column3], ...) VALUES (?, ?, ?, ...)'- UPDATE: 'UPDATE [table] SET [column1] = ?, [column2] = ?, ... WHERE [column3] = ?'- DELETE: 'DELETE FROM [table] WHERE [column1] = ? AND [column2] = ? OR ...'- ALTER: 'ALTER TABLE [table] ADD COLUMN [column1] [datatype] {DEFAULT [value]}'- DROP: 'DROP TABLE [table]' |
| [`DocumentTextAdapter`](#documenttextadapter-in-pydagadaptersdocumentsdocumenttextadapterpy) | `Adapter` that retrieves text content from specified files         |
| [`DocxAdapter`](#docxadapter-in-pydagadaptersdocumentsdocxadapterpy) | `Adapter` for writing data to DOCX documents.The specified addresses in `write_to_sink` can be used to map data keys from buffer to place holders in word template.If no addresses are specified all buffer keys are directly mapped to the context of the word template |
| [`NpzAdapter`](#npzadapter-in-pydagadaptersdocumentsnpzadapterpy) | `Adapter` that retrieves data from a *.npz numpy file         |
| [`HttpAdapter`](#httpadapter-in-pydagadaptershttphttpadapterpy) | `Adapter` for reading and writing data from/to http endpoints     |
| [`MQTTAdapter`](#mqttadapter-in-pydagadaptersmqttmqttadapterpy) | `Adapter` for subscribing or writing data from/to MQTT topics.     |
| [`OpcUaAdapter`](#opcuaadapter-in-pydagadaptersopcuaopcuaadapterpy) | `Adapter` for reading and writing data from/to OPC UA servers.     |
| [`S7Adapter`](#s7adapter-in-pydagadapterss7s7adapterpy) | `Adapter`reading from and writing to S7 PLCs.     |
| [`ByteStreamAdapter`](#bytestreamadapter-in-pydagadapterssocketbytestreamadapterpy) | `Adapter` to read and write byte streams from/to a socket connection.<br>The adapter can be configured with different byte schemas for connecting, disconnecting,sending, and receiving data.<br>The bytescheams are defined as a string of data types, e.g. "Bhf5s" -> uint8, int16, float32, string of length 5<br>The addresses in read_from_source and write_to_sink are used to specify the buffer keys to read from or write to.<br>e.g. addresses = ["B1", "B3", "SENSOR1"]<br>The length of the addresses list must not match the number of buffers passed, all buffers are being searched for the keys in addresses.But it has to match the number of elements in the schema used for reading or writing. Omiting schema fields can be done by specifying None in the addresses list.<br>For Example:<br>schema = "BfI" -> addresses = ["ID1", None, "ID3"] |
| [`SerialAdapter`](#serialadapter-in-pydagadapterssocketserialadapterpy) | `Adapter` for serial communication using pySerial.     |
| [`TCPClientAdapter`](#tcpclientadapter-in-pydagadapterssockettcpclientadapterpy) |  |
| [`WebSocketAdapter`](#websocketadapter-in-pydagadapterssocketwebsocketadapterpy) | `Adapter` for subscribing and writing data from/to WebSocket endpoints.     |
| [`VSEAdapter`](#vseadapter-in-pydagadapterssocketifmvsevseadapterpy) |  |
| [`WebcamAdapter`](#webcamadapter-in-pydagadaptersvisionwebcamadapterpy) | An `Adapter` that captures webcam video feed into a `Buffer`     |



## `Adapter` (in `pydag\adapters\Adapter.py`)

Abstract base class for `Adapters`. All `Adapters` must inherit from this class.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `Adapter`
from pydag.adapters.Adapter import Adapter  # Adjust import if needed

obj = Adapter()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `PublishAdapter` (in `pydag\adapters\PublishAdapter.py`)

abstract class for `Adapter` Interface for publishing to data sinks.
<br>new `Adapters` that allow for publishing to a sink via callback must inherit this class next to `Adapter`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `PublishAdapter`
from pydag.adapters.PublishAdapter import PublishAdapter  # Adjust import if needed

obj = PublishAdapter()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `ReadAdapter` (in `pydag\adapters\ReadAdapter.py`)

abstract class for `Adapter` Interface for reading from data sources.
<br>new `Adapters` that allow for reading from a source via one-shot polling must inherit this class next to `Adapter`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `ReadAdapter`
from pydag.adapters.ReadAdapter import ReadAdapter  # Adjust import if needed

obj = ReadAdapter()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `SubscribeAdapter` (in `pydag\adapters\SubscribeAdapter.py`)

abstract class for `Adapter` Interface for subscribing from data sources
<br>new `Adapters` that allow for subscribing to a source via callback must inherit this class next to `Adapter`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `SubscribeAdapter`
from pydag.adapters.SubscribeAdapter import SubscribeAdapter  # Adjust import if needed

obj = SubscribeAdapter()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `WriteAdapter` (in `pydag\adapters\WriteAdapter.py`)

abstract class for Adapter Interface for writing to data sinks
<br>new `Adapters` that allow for writing to a sink via one-shot polling must inherit this class next to `Adapter`.
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `WriteAdapter`
from pydag.adapters.WriteAdapter import WriteAdapter  # Adjust import if needed

obj = WriteAdapter()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `AdsAdapter` (in `pydag\adapters\ads\AdsAdapter.py`)

`Adapter` for reading and writing data from/to Beckhoff TwinCAT PLCs via ADS (Automation Device Specification).
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `ams_net_id` | `str` | `` | AMS Net Id to connect to for ADS Connection |
| `twincat` | `int` | `3` | Twincat version to use, e.g. 2 or 3 for TwinCAT 2/3 |


```python
# Example usage of `AdsAdapter`
from pydag.adapters.ads.AdsAdapter import AdsAdapter  # Adjust import if needed

obj = AdsAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.ams_net_id="<string>"
obj.twincat=3
```

[Go to Summary](#summary)
## `AudioAdapter` (in `pydag\adapters\audio\AudioAdapter.py`)

`Adapter` for subscribing to a system's audio input channels (e.g. from a USB microphone) using the `sounddevice` library.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `sample_rate` | `int` | `44100` | sample rate of audio channel, usually 44100 Hz |
| `device` | `int` | `` | device number to use as input stream, if nothing is specified the default device is used |


```python
# Example usage of `AudioAdapter`
from pydag.adapters.audio.AudioAdapter import AudioAdapter  # Adjust import if needed

obj = AudioAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.sample_rate=44100
obj.device=1
```

[Go to Summary](#summary)
## `SolidPDMAdapter` (in `pydag\adapters\cad\SolidPDMAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `SolidPDMAdapter`
from pydag.adapters.cad.SolidPDMAdapter import SolidPDMAdapter  # Adjust import if needed

obj = SolidPDMAdapter()
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `CsvReadAdapter` (in `pydag\adapters\csv\CsvReadAdapter.py`)

`Adapter` for reading data from CSV files.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `file_path` | `str` | `` | path to the csv file to read |
| `mode` | `str` | `'CSVReadMode.ONE_AT_A_TIME.value'` | read mode: ALL_AT_ONCE|ONE_AT_A_TIME|LOOP |
| `delimiter` | `str` | `';'` | delimiter to use to separate columns |
| `has_header` | `bool` | `True` | specifies whether a header is present in data |
| `auto_detect` | `bool` | `False` | specifies whether to use the csv sniffing option |
| `force_numeric` | `bool` | `True` | forces numeric parsing of data |


```python
# Example usage of `CsvReadAdapter`
from pydag.adapters.csv.CsvReadAdapter import CsvReadAdapter  # Adjust import if needed

obj = CsvReadAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.file_path="path/to/file.txt"
obj.mode='CSVReadMode.ONE_AT_A_TIME.value'
obj.delimiter=';'
obj.has_header=True
obj.auto_detect=False
obj.force_numeric=True
```

[Go to Summary](#summary)
## `CsvWriteAdapter` (in `pydag\adapters\csv\CsvWriteAdapter.py`)

`Adapter` for writing data to CSV files.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `folder` | `str` | `` | folder to save the csv files to |
| `file_post_fix` | `str` | `` | postfix to use with every file |
| `file_extension` | `str` | `'csv'` | extension of the files being created, specify without *.*, e.g. 'csv' or 'txt' |
| `max_samples` | `int` | `1000000` | maximum number of samples in one file, if limit is reached a new file is being created |
| `delimiter` | `str` | `';'` | delimiter to use for column separation |
| `decimal_precision` | `int` | `3` | maximum decimal precision of numeric values |


```python
# Example usage of `CsvWriteAdapter`
from pydag.adapters.csv.CsvWriteAdapter import CsvWriteAdapter  # Adjust import if needed

obj = CsvWriteAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.folder="path/to/folder"
obj.file_post_fix="path/to/file.txt"
obj.file_extension='csv'
obj.max_samples=1000000
obj.delimiter=';'
obj.decimal_precision=3
```

[Go to Summary](#summary)
## `InfluxDbAdapter` (in `pydag\adapters\db\InfluxDbAdapter.py`)

`Adapter` thats reads or writes to InfluxDB.
<br>Address Schema:
<br>address = "b=[bucket];m=[measurement];f=[field]"
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `endpoint` | `str` | `'http://localhost:8086'` | The endpoint URL for the InfluxDB instance. |
| `token` | `str` | `` | The authentication token for InfluxDB. |
| `org` | `str` | `'my-org'` | The organization name in InfluxDB. |


```python
# Example usage of `InfluxDbAdapter`
from pydag.adapters.db.InfluxDbAdapter import InfluxDbAdapter  # Adjust import if needed

obj = InfluxDbAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.endpoint='http://localhost:8086'
obj.token="<string>"
obj.org='my-org'
```

[Go to Summary](#summary)
## `SQLAdapter` (in `pydag\adapters\db\SQLAdapter.py`)

`Adapter` for reading and writing data from/to SQL databases using pyodbc.
<br>Required ODBC driver must be installed for the specific SQL database (e.g. MySQL, PostgreSQL, SQLite, etc.) and system
<br><br>The `addresses` in `_on_write` and `_on_read` is used to specify the SQL statement to execute. SQL statements should adhere the following format:
- SELECT: 'SELECT [column1], [column2], ... FROM [table] WHERE [column3] = [value1]'
- CREATE TABLE: 'CREATE TABLE ...'        
- INSERT: 'INSERT INTO [table] ([column1], [column2], [column3], ...) VALUES (?, ?, ?, ...)'
- UPDATE: 'UPDATE [table] SET [column1] = ?, [column2] = ?, ... WHERE [column3] = ?'
- DELETE: 'DELETE FROM [table] WHERE [column1] = ? AND [column2] = ? OR ...'
- ALTER: 'ALTER TABLE [table] ADD COLUMN [column1] [datatype] {DEFAULT [value]}'
- DROP: 'DROP TABLE [table]'
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `connection_str` | `str` | `` | connection string for the specific SQL database |


```python
# Example usage of `SQLAdapter`
from pydag.adapters.db.SQLAdapter import SQLAdapter  # Adjust import if needed

obj = SQLAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.connection_str="<string>"
```

[Go to Summary](#summary)
## `DocumentTextAdapter` (in `pydag\adapters\documents\DocumentTextAdapter.py`)

`Adapter` that retrieves text content from specified files
    
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `file_path` | `str` | `` | the path to a file or a folder, that shall be screened for document texts |


```python
# Example usage of `DocumentTextAdapter`
from pydag.adapters.documents.DocumentTextAdapter import DocumentTextAdapter  # Adjust import if needed

obj = DocumentTextAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.file_path="path/to/file.txt"
```

[Go to Summary](#summary)
## `DocxAdapter` (in `pydag\adapters\documents\DocxAdapter.py`)

`Adapter` for writing data to DOCX documents.

The specified addresses in `write_to_sink` can be used to map data keys from buffer to place holders in word template.
If no addresses are specified all buffer keys are directly mapped to the context of the word template
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `output_path` | `str` | `'output.docx'` |  |
| `template_path` | `str` | `` |  |


```python
# Example usage of `DocxAdapter`
from pydag.adapters.documents.DocxAdapter import DocxAdapter  # Adjust import if needed

obj = DocxAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.output_path='output.docx'
obj.template_path="<string>"
```

[Go to Summary](#summary)
## `NpzAdapter` (in `pydag\adapters\documents\NpzAdapter.py`)

`Adapter` that retrieves data from a *.npz numpy file
    
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `file_path` | `str` | `` | the path to a file or a folder, that shall be screened for document texts |


```python
# Example usage of `NpzAdapter`
from pydag.adapters.documents.NpzAdapter import NpzAdapter  # Adjust import if needed

obj = NpzAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.file_path="path/to/file.txt"
```

[Go to Summary](#summary)
## `HttpAdapter` (in `pydag\adapters\http\HttpAdapter.py`)

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
from pydag.adapters.http.HttpAdapter import HttpAdapter  # Adjust import if needed

obj = HttpAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.base_url="https://example.com"
obj.headers="<string>"
obj.json_path=False
```

[Go to Summary](#summary)
## `MQTTAdapter` (in `pydag\adapters\mqtt\MQTTAdapter.py`)

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
from pydag.adapters.mqtt.MQTTAdapter import MQTTAdapter  # Adjust import if needed

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

[Go to Summary](#summary)
## `OpcUaAdapter` (in `pydag\adapters\opcua\OpcUaAdapter.py`)

`Adapter` for reading and writing data from/to OPC UA servers.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `endpoint` | `str` | `` | endpoint of the opc ua server, e.g. opc.tcp://localhost:48010 |


```python
# Example usage of `OpcUaAdapter`
from pydag.adapters.opcua.OpcUaAdapter import OpcUaAdapter  # Adjust import if needed

obj = OpcUaAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.endpoint="<string>"
```

[Go to Summary](#summary)
## `S7Adapter` (in `pydag\adapters\s7\S7Adapter.py`)

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
from pydag.adapters.s7.S7Adapter import S7Adapter  # Adjust import if needed

obj = S7Adapter()
obj.id="<string>"
obj.load_on_install=False
obj.host='127.0.0.1'
obj.rack=0
obj.slot=1
```

[Go to Summary](#summary)
## `ByteStreamAdapter` (in `pydag\adapters\socket\ByteStreamAdapter.py`)

`Adapter` to read and write byte streams from/to a socket connection.
<br>The adapter can be configured with different byte schemas for connecting, disconnecting,
sending, and receiving data.
<br>The bytescheams are defined as a string of data types, e.g. "Bhf5s" -> uint8, int16, float32, string of length 5
<br>The addresses in read_from_source and write_to_sink are used to specify the buffer keys to read from or write to.
<br>e.g. addresses = ["B1", "B3", "SENSOR1"]
<br>The length of the addresses list must not match the number of buffers passed, all buffers are being searched for the keys in addresses.
But it has to match the number of elements in the schema used for reading or writing. Omiting schema fields can be done by specifying None in the addresses list.
<br>For Example:
<br>schema = "BfI" -> addresses = ["ID1", None, "ID3"]
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `host` | `str` | `` | name of the host to connect to, e.g. IP address or COM-Port |
| `port` | `int` | `` | port of the host to connect to, in case of Serial Protocol this is ignored |
| `timeout` | `int` | `1` | timeout in seconds for connecting to the host |
| `connect_bytes` | `bytes` | `` | bytes to send after each connection |
| `disconnect_bytes` | `bytes` | `` | bytes to send before each disconnection |
| `before_send_bytes` | `bytes` | `` | bytes to send before each send |
| `after_send_bytes` | `bytes` | `` | bytes to send after each send |
| `before_receive_bytes` | `bytes` | `` | bytes to send before each receive |
| `after_receive_bytes` | `bytes` | `` | bytes to send after each receive |
| `read_byte_schema` | `str` | `` | schema of bytes to convert the received data to and store in buffers, e.g. s20iiff (string of length 20, int, int, float, float) |
| `write_byte_schema` | `str` | `` | schema of bytes to convert the buffers data to and send it, e.g. ddfs10 (double, double, float, string of length 10) |


```python
# Example usage of `ByteStreamAdapter`
from pydag.adapters.socket.ByteStreamAdapter import ByteStreamAdapter  # Adjust import if needed

obj = ByteStreamAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.host="<string>"
obj.port=1
obj.timeout=1
obj.connect_bytes="<value>"
obj.disconnect_bytes="<value>"
obj.before_send_bytes="<value>"
obj.after_send_bytes="<value>"
obj.before_receive_bytes="<value>"
obj.after_receive_bytes="<value>"
obj.read_byte_schema="<string>"
obj.write_byte_schema="<string>"
```

[Go to Summary](#summary)
## `SerialAdapter` (in `pydag\adapters\socket\SerialAdapter.py`)

`Adapter` for serial communication using pySerial.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `host` | `str` | `` | name of the host to connect to, e.g. IP address or COM-Port |
| `port` | `int` | `` | port of the host to connect to, in case of Serial Protocol this is ignored |
| `timeout` | `int` | `1` | timeout in seconds for connecting to the host |
| `connect_bytes` | `bytes` | `` | bytes to send after each connection |
| `disconnect_bytes` | `bytes` | `` | bytes to send before each disconnection |
| `before_send_bytes` | `bytes` | `` | bytes to send before each send |
| `after_send_bytes` | `bytes` | `` | bytes to send after each send |
| `before_receive_bytes` | `bytes` | `` | bytes to send before each receive |
| `after_receive_bytes` | `bytes` | `` | bytes to send after each receive |
| `read_byte_schema` | `str` | `` | schema of bytes to convert the received data to and store in buffers, e.g. s20iiff (string of length 20, int, int, float, float) |
| `write_byte_schema` | `str` | `` | schema of bytes to convert the buffers data to and send it, e.g. ddfs10 (double, double, float, string of length 10) |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `baud_rate` | `int` | `9600` | baud rate for serial communication |
| `new_line_mode` | `bool` | `True` | whether to use new line mode for parsing serial communication |
| `delimiter` | `str` | `';'` | delimiter to use in new line mode |


```python
# Example usage of `SerialAdapter`
from pydag.adapters.socket.SerialAdapter import SerialAdapter  # Adjust import if needed

obj = SerialAdapter()
obj.host="<string>"
obj.port=1
obj.timeout=1
obj.connect_bytes="<value>"
obj.disconnect_bytes="<value>"
obj.before_send_bytes="<value>"
obj.after_send_bytes="<value>"
obj.before_receive_bytes="<value>"
obj.after_receive_bytes="<value>"
obj.read_byte_schema="<string>"
obj.write_byte_schema="<string>"
obj.id="<string>"
obj.load_on_install=False
obj.baud_rate=9600
obj.new_line_mode=True
obj.delimiter=';'
```

[Go to Summary](#summary)
## `TCPClientAdapter` (in `pydag\adapters\socket\TCPClientAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `host` | `str` | `` | name of the host to connect to, e.g. IP address or COM-Port |
| `port` | `int` | `` | port of the host to connect to, in case of Serial Protocol this is ignored |
| `timeout` | `int` | `1` | timeout in seconds for connecting to the host |
| `connect_bytes` | `bytes` | `` | bytes to send after each connection |
| `disconnect_bytes` | `bytes` | `` | bytes to send before each disconnection |
| `before_send_bytes` | `bytes` | `` | bytes to send before each send |
| `after_send_bytes` | `bytes` | `` | bytes to send after each send |
| `before_receive_bytes` | `bytes` | `` | bytes to send before each receive |
| `after_receive_bytes` | `bytes` | `` | bytes to send after each receive |
| `read_byte_schema` | `str` | `` | schema of bytes to convert the received data to and store in buffers, e.g. s20iiff (string of length 20, int, int, float, float) |
| `write_byte_schema` | `str` | `` | schema of bytes to convert the buffers data to and send it, e.g. ddfs10 (double, double, float, string of length 10) |
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |


```python
# Example usage of `TCPClientAdapter`
from pydag.adapters.socket.TCPClientAdapter import TCPClientAdapter  # Adjust import if needed

obj = TCPClientAdapter()
obj.host="<string>"
obj.port=1
obj.timeout=1
obj.connect_bytes="<value>"
obj.disconnect_bytes="<value>"
obj.before_send_bytes="<value>"
obj.after_send_bytes="<value>"
obj.before_receive_bytes="<value>"
obj.after_receive_bytes="<value>"
obj.read_byte_schema="<string>"
obj.write_byte_schema="<string>"
obj.id="<string>"
obj.load_on_install=False
```

[Go to Summary](#summary)
## `WebSocketAdapter` (in `pydag\adapters\socket\WebSocketAdapter.py`)

`Adapter` for subscribing and writing data from/to WebSocket endpoints.
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `url` | `str` | `` | socket url, e.g. wss://localhost:10001 |


```python
# Example usage of `WebSocketAdapter`
from pydag.adapters.socket.WebSocketAdapter import WebSocketAdapter  # Adjust import if needed

obj = WebSocketAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.url="https://example.com"
```

[Go to Summary](#summary)
## `VSEAdapter` (in `pydag\adapters\socket\ifmvse\VSEAdapter.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `host` | `str` | `'192.168.0.1'` | ip address or host name of the vse host device |
| `port` | `int` | `3321` | port of the vse host device |
| `sensor` | `int` | `1` | sensor number to measure |
| `sample_rate` | `int` | `10000` | sample rate in Hz from 1.000 Hz to 100.000 Hz |


```python
# Example usage of `VSEAdapter`
from pydag.adapters.socket.ifmvse.VSEAdapter import VSEAdapter  # Adjust import if needed

obj = VSEAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.host='192.168.0.1'
obj.port=3321
obj.sensor=1
obj.sample_rate=10000
```

[Go to Summary](#summary)
## `WebcamAdapter` (in `pydag\adapters\vision\WebcamAdapter.py`)

An `Adapter` that captures webcam video feed into a `Buffer`
    
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | `` | unique identifier of element in DataGrabber application |
| `load_on_install` | `bool` | `False` | specifies whether the GrabberElement should try to load from local json config file on install |
| `camera_index` | `int` | `0` | indexof installed cameras |
| `resolution` | `list[int]` | `'list()'` | resolution [width, height] |
| `fps` | `int` | `30` | frames per second |
| `codec` | `str` | `'MJPG'` | video codec to use, mp4v | MJPG | H264 | XVID |
| `encode_base64` | `bool` | `False` | if set to true, the image data is converted to base64 strings |
| `data_uri_prefix` | `str` | `'data:image/jpeg;base64,'` | data URI prefix for base64 images |


```python
# Example usage of `WebcamAdapter`
from pydag.adapters.vision.WebcamAdapter import WebcamAdapter  # Adjust import if needed

obj = WebcamAdapter()
obj.id="<string>"
obj.load_on_install=False
obj.camera_index=0
obj.resolution='list()'
obj.fps=30
obj.codec='MJPG'
obj.encode_base64=False
obj.data_uri_prefix='data:image/jpeg;base64,'
```

[Go to Summary](#summary)