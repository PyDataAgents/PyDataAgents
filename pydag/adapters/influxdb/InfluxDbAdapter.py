from dataclasses import dataclass, field
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

from ...adapters.AdapterException import AdapterException
from ...adapters.ReadAdapter import ReadAdapter
from ...adapters.WriteAdapter import WriteAdapter
from ...buffers.Buffer import Buffer
from ...buffers.DictBuffer import DictBuffer
from ...buffers.ListBuffer import ListBuffer
from ...buffers.TimedBuffer import TimedBuffer
from ...utils.AdapterUtils import AdapterUtils

BUCKET = "b"
MEASUREMENT = "m"
FIELD = "f"

@dataclass
class InfluxDbAdapter(ReadAdapter, WriteAdapter):
    """`Adapter` thats reads or writes to InfluxDB.
    Address Schema:
    address = "b=<bucket>;m=<measurement>;f=<field>"
    """
    
    endpoint : str = field(default="http://localhost:8086", metadata={"description": "The endpoint URL for the InfluxDB instance."})
    token : str = field(default=None, metadata={"description": "The authentication token for InfluxDB."})
    org : str = field(default="my-org", metadata={"description": "The organization name in InfluxDB."})

    def __init__(self):
        super().__init__()
        self.client : influxdb_client.InfluxDBClient = None  # Placeholder for InfluxDB client initialization

    def connect(self) -> bool:
        self.client = influxdb_client.InfluxDBClient(url=self.endpoint, token=self.token, org=self.org)
        return True
            
    def disconnect(self) -> bool:
        self.client = None
        return False

    def read_from_source(self, buffers : dict[str, Buffer], addresses : list[str], n : int):
        if len(buffers) == len(addresses):
            a = 0
            query_api = self.client.query_api()
            for buffer in buffers.values():
                address = addresses[a]
                d_address = AdapterUtils.address_to_dict(address)
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
                                d_record = {"t-" + f : record.get_time(), f : record.get_value()} 
                                buffer.push(d_record)
                else:
                     raise AdapterException("Invalid address format. Expected format: b=<BUCKET>;m=<MEASUREMENT>;f=<FIELD>")
                a += 1
        else:
            raise AdapterException("The number of buffers and addresses must match.")
    
    def write_to_sink(self, buffers : dict[str, Buffer], addresses : list[str], n : int, persistent : bool):
        if len(buffers) == len(addresses):
            a = 0
            write_api = self.client.write_api(write_options=SYNCHRONOUS)
            for buffer in buffers.values():
                if buffer.size() == 0:
                    continue
                address = addresses[a]
                d_address = AdapterUtils.address_to_dict(address)
                if "b" in d_address and "m" in d_address and "f" in d_address:
                    bucket = d_address["b"]
                    measurement = d_address["m"]
                    field = d_address["f"]
                    if isinstance(buffer, DictBuffer):
                        raise AdapterException("DictBuffer is not supported for writing to InfluxDB. Use ListBuffer or TimedBuffer instead.")                    
                    elif isinstance(buffer, TimedBuffer):
                        data = buffer.data(n = n, persistent=persistent)
                        val = data["values"]
                    elif isinstance(buffer, ListBuffer):
                        val = buffer.data(n = n, persistent=persistent)
                    else:
                        raise AdapterException("Unsupported buffer type. Use ListBuffer or TimedBuffer for writing to InfluxDB.")
                    if n > 1:
                        p = []
                        for v in val:
                            p.append(influxdb_client.Point(measurement).field(field, v))
                    else:
                        p = influxdb_client.Point(measurement).field(field, val[0])
                    # write all points to sink
                    write_api.write(bucket = bucket, org=self.org, record=p)                                          
                else:
                     raise AdapterException("Invalid address format. Expected format: b=<BUCKET>;m=<MEASUREMENT>;f=<FIELD>")
                a += 1
        else:
            raise AdapterException("The number of buffers and addresses must match.")

    