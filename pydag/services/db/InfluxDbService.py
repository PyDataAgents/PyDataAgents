from dataclasses import dataclass, field
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


from ...services.MappingService import MappingService
from ..ServiceException import ServiceException
from ..ReadService import ReadService
from ..WriteService import WriteService
from ...agents.Agent import Agent
from ...buffers.DictBuffer import DictBuffer
from ...buffers.ListBuffer import ListBuffer
from ...buffers.TimedBuffer import TimedBuffer


BUCKET = "b"
MEASUREMENT = "m"
FIELD = "f"

@dataclass
class InfluxDbService(ReadService, WriteService):
    """`MappingService` thats reads or writes to InfluxDB.
    <br>Address Schema:
    <br>address = "b=[bucket];m=[measurement];f=[field]"
    """
    
    endpoint : str = field(default="http://localhost:8086", metadata={"description": "The endpoint URL for the InfluxDB instance."})
    token : str = field(default=None, metadata={"description": "The authentication token for InfluxDB."})
    org : str = field(default="my-org", metadata={"description": "The organization name in InfluxDB."})

    def __post_init__(self):
        super().__post_init__()
        self._client : influxdb_client.InfluxDBClient = None  # Placeholder for InfluxDB client initialization

    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._client = influxdb_client.InfluxDBClient(url=self.endpoint, token=self.token, org=self.org)
        if not self._client.ping():
            raise ServiceException("Failed to connect to InfluxDB")

    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
        self._client = None        
    
    def _read_from_source(self):
        if len(self.get_buffers()) == len(self.addresses):
            a = 0
            query_api = self._client.query_api()
            for buffer in self.get_buffers().values():
                address = self.addresses[a]
                d_address = MappingService.address_to_dict(address)
                if BUCKET in d_address and MEASUREMENT in d_address and FIELD in d_address:
                    b = d_address["b"]
                    m = d_address["m"]
                    f = d_address["f"]
                    s = 0
                    if "s" in d_address:
                        s = d_address["s"]
                    query = f"""
                            from(bucket: "{b}") 
                            |> range(start: {s}) 
                            |> filter(fn: (r) => r._measurement == "{m}"
                               and r._field == "{f}")
                        """
                    result = query_api.query(query, org=self.org)
                    if isinstance(buffer, ListBuffer):
                        for table in result:
                            for record in table.records:
                                buffer.push(record.get_value())
                    elif isinstance(buffer, DictBuffer):
                        for table in result:
                            for record in table.records:
                                d_record = {"t-" + f: record.get_time(), f: record.get_value()}
                                buffer.push(d_record)
                else:
                    raise ServiceException("Invalid address format. Expected format: b=<BUCKET>;m=<MEASUREMENT>;f=<FIELD>")
                a += 1
        else:
            raise ServiceException("The number of buffers and addresses must match.")
    
    def _write_to_sink(self):
        if len(self.get_buffers()) == len(self.addresses):
            a = 0
            write_api = self._client.write_api(write_options=SYNCHRONOUS)
            for buffer in self.get_buffers().values():
                if buffer.size() == 0:
                    continue
                address = self.addresses[a]
                d_address = MappingService.address_to_dict(address)
                if "b" in d_address and "m" in d_address and "f" in d_address:
                    bucket = d_address["b"]
                    measurement = d_address["m"]
                    fld = d_address["f"]
                    if isinstance(buffer, DictBuffer):
                        raise ServiceException("DictBuffer is not supported for writing to InfluxDB. Use ListBuffer or TimedBuffer instead.")                    
                    elif isinstance(buffer, TimedBuffer):
                        data = buffer.data(n = self.n, persistent=self.persistent)
                        val = data["values"]
                    elif isinstance(buffer, ListBuffer):
                        val = buffer.data(n = self.n, persistent=self.persistent)
                    else:
                        raise ServiceException("Unsupported buffer type. Use ListBuffer or TimedBuffer for writing to InfluxDB.")
                    if self.n > 1:
                        p = []
                        for v in val:
                            p.append(influxdb_client.Point(measurement).field(fld, v))
                    else:
                        p = influxdb_client.Point(measurement).field(fld, val[0])
                    # write all points to sink
                    write_api.write(bucket = bucket, org=self.org, record=p)                                          
                else:
                    raise ServiceException("Invalid address format. Expected format: b=<BUCKET>;m=<MEASUREMENT>;f=<FIELD>")
                a += 1
        else:
            raise ServiceException("The number of buffers and addresses must match.")

    