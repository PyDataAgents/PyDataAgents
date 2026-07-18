from dataclasses import dataclass, field
import json
import paho.mqtt.client as mqtt


from ..ServiceException import ServiceException
from ..SubscribeService import SubscribeService
from ..WriteService import WriteService
from ...agents.Agent import Agent
from ...utils.StringUtils import StringUtils


ROOT_TOPIC = "#"

@dataclass
class MQTTService(SubscribeService, WriteService):
    """`MappingService` for subscribing or writing data from/to MQTT topics.
    """
    
    endpoint : str = field(default=None, metadata={"description": "endpoint of the MQTT broker, e.g. test.mosquitto.org (public test broker)"})
    port : int = field(default=1883, metadata={"description": "port of the mqtt broker"})
    keep_alive : int = field(default=60, metadata={"description": "keep alive interval with broker"})
    force_numeric : bool = field(default=False, metadata={"description": "specifies if the payload from mqtt topics should be parsed as numeric value, rather than string"})
    retain : bool = field(default=False, metadata={"description": "specifies whether messages should be retained on publishing"})
    qos : int = field(default=0, metadata={"description": "quality of service parameter of mqtt publish"})
    
    def __post_init__(self):
        super().__post_init__()
        self._client : mqtt.Client = None
    
    def _on_install(self, agent : Agent = None):
        self._client = mqtt.Client()
        if self._client.connect(self.endpoint, self.port, self.keep_alive):
            raise ServiceException(f"Connection to MQTT broker failed in {self.__class__.__name__}")
        
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        if self._client:
            self._client.disconnect()
        
    def subscribe(self):
        """subscribe to mqtt topics by specifying addresses in the schema of address = "topic=this/is/a/topic;id=buf1"
            <br>where id is the buffer id, where this topic's messages shall be stored to
        """
        if self.n > 1:
            raise ServiceException("n > 1 is not implemented yet")
        topic_to_buffer = dict()        
        for address in self.addresses:
            d = StringUtils.string_to_dict(address)
            if "topic" not in d or "id" not in d:
                raise ServiceException("mqtt address must contain topic=<MQTT_TOPIC> and id=<BUFFER_ID>")
            topic = d["topic"]
            id = d["id"]
            topic_to_buffer[topic] = id
            if self._client:
                self._client.subscribe(topic)
            
        # define a message callback inline
        def on_message(client, userdata, message):
            print(f"Received: {message.payload.decode()} on topic {message.topic}")
            if message.topic in topic_to_buffer:
                if self.force_numeric:
                    self.get_buffers()[topic_to_buffer[message.topic]].push(float(message.payload.decode()))
                else:
                    self.get_buffers()[topic_to_buffer[message.topic]].push(message.payload.decode())
               
        if self._client:
            self._client.on_message = on_message
            self._client.loop_start()
        
    def unsubscribe(self):
        if self._client:
            self._client.unsubscribe(ROOT_TOPIC)
    
    def write_to_sink(self):
        """publish buffer values to mqtt topcis by writing single publish messages

        Raises:
            ServiceException: _description_
        """
        if len(self.get_buffers()) is not len(self.addresses):
            raise ServiceException("length of buffers and addresses must be the same in " + self.__class__.__name__)
        a = 0
        for buffer in self.get_buffers().values():
            address = self.addresses[a]
            data = buffer.data(n = self.n, persistent = self.persistent)
            if self.force_numeric:
                values = data['values']
                if len(values) > 1:
                    val = json.dumps(values)
                else:
                    val = float(values[0])
            else:
                val = json.dumps(data)
            if self._client:
                self._client.publish(address, val, retain = self.retain, qos = self.qos)
            a = a + 1