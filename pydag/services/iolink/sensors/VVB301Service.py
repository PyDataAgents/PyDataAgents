from dataclasses import dataclass, field


from pydag.agents.Agent import Agent
from pydag.buffers.Buffer import Buffer
from pydag.services.ReadService import ReadService
from pydag.services.iolink.sensors.VVB301.blob_data_receivers import RawDataCacher
from pydag.services.iolink.sensors.VVB301.definitions import MeasuringAxis, VVBType
from pydag.services.iolink.sensors.VVB301.iol_device_request import IolDeviceRequest
from pydag.services.iolink.sensors.VVB301.task_blob_data import QueryBlobDataTask

@dataclass
class VVB301Service(ReadService):
    """ A `MappingService` that reads BLOB data from IOLink Device VVB301    
    """
    
    host : str = field(default=None, metadata={"description": "name of the IOLink host"})
    port : int = field(default = 1, metadata={"description": "port number of the connected VVB301 device"})
    
    def __post_init__(self):
        super().__post_init__()
        self.receiver = None
        self.req_builder = None
        self.query_raw_data = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self.receiver = RawDataCacher()
        self.receiver.set_measuring_axis(MeasuringAxis.XYZ_AXIS_EACH_4S)
        # this component is needed by the blob task below to construct the various requests dictated by the workflow of querying raw data from the device
        self.req_builder = IolDeviceRequest(VVBType.VVB301, self.port)
        # 3. Both raw data and history data get transmitted via the Blob transfer workflow specified in the IOL specification. The specific receiver helps diferentiate between them
        self.query_raw_data = QueryBlobDataTask(self.req_builder, self.host, self.receiver)       
    
    def read_from_source(self):
        self.query_raw_data.run()
        data = self.receiver.get_data()
        buffer : Buffer = next(iter(self.get_buffers().values()))
        buffer.push(data)

    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        self.receiver = None
        self.req_builder = None
        self.query_raw_data = None