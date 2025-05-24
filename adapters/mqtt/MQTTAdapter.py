from dataclasses import dataclass, field
import paho.mqtt.client as mqtt
from PyDataGrabber.adapters.AdapterException import AdapterException
from PyDataGrabber.adapters.SubscribeAdapter import SubscribeAdapter
from PyDataGrabber.adapters.WriteAdapter import WriteAdapter
from PyDataGrabber.buffers.Buffer import Buffer
from PyDataGrabber.utils.StringUtils import StringUtils

ROOT_TOPIC = "#"

@dataclass
class MQTTAdapter(SubscribeAdapter, WriteAdapter):
    
    endpoint : str = field(default=None, metadata={"description": "endpoint of the MQTT broker, e.g. test.mosquitto.org (public test broker)"})
    port : int = field(default=1883, metadata={"description": "port of the mqtt broker"})
    keep_alive : int = field(default=60, metadata={"description": "keep alive interval with broker"})
    force_numeric : bool = field(default=False, metadata={"description": "specifies if the payload from mqtt topics should be parsed as numeric value, rather than string"})
    retain : bool = field(default=False, metadata={"description": "specifies whether messages should be retained on publishing"})
    qos : int = field(default=0, metadata={"description": "quality of service parameter of mqtt publish"})
    
    def __init__(self):
        super().__init__()
        self.client : mqtt.Client = None
    
    def connect(self) -> bool:
        self.client = mqtt.Client()
        self.client.connect(self.endpoint, self.port, self.keep_alive)
        return True
            
    def disconnect(self) -> bool:
        self.client.disconnect()
        return True
    
    def subscribe(self, buffers : dict[str, Buffer], addresses : list[str], sampling_period : int = 0, n : int = 1):
        """subscribe to mqtt topics by specifying addresses in the schema of address = "topic=this/is/a/topic;id=buf1"
            <br>where id is the buffer id, where this topic's messages shall be stored to
        Args:
            buffers (dict[str, Buffer]): _description_
            addresses (list[str]): _description_
            sampling_period (int, optional): _description_. Defaults to 0.
            n (int, optional): _description_. Defaults to 1.
        """
        if n > 1:
            raise AdapterException("n > 1 is not implemented yet")
        topic_to_buffer = dict()        
        for address in addresses:
            d = StringUtils.string_to_dict(address)
            if "topic" not in d or "id" not in d:
                raise AdapterException("mqtt address must contain topic=<MQTT_TOPIC> and id=<BUFFER_ID>")
            topic = d["topic"]
            id = d["id"]
            topic_to_buffer[topic] = id
            self.client.subscribe(topic)
            
        # define a message callback inline
        def on_message(client, userdata, message):
            print(f"Received: {message.payload.decode()} on topic {message.topic}")
            if message.topic in topic_to_buffer:
                if self.force_numeric:
                    buffers[topic_to_buffer[message.topic]].push(float(message.payload.decode()))
                else:
                    buffers[topic_to_buffer[message.topic]].push(message.payload.decode())
               
        self.client.on_message = on_message
        self.client.loop_start()
        
    def unsubscribe(self):
        self.client.unsubscribe(ROOT_TOPIC)
    
    def write_to_sink(self, buffers : dict[str, Buffer], addresses : list[str], n : int = 1, persistent : bool = True):
        """publish buffer values to mqtt topcis by writing single publish messages

        Args:
            buffers (dict[str, Buffer]): dictionary of buffers
            addresses (list[str]): list of topics to write to
            n (int, optional): number of samples to extract from buffer. Defaults to 1.
            persistent (bool, optional): specifies whether to keep values in buffer after writing to sink. Defaults to True.

        Raises:
            AdapterException: _description_
        """
        if len(buffers) is not len(addresses):
            raise AdapterException("length of buffers and addresses must be the same in " + self.name())
        a = 0
        for buffer in buffers.values():
            address = addresses[a]
            val = buffer.data(n = n, persistent = persistent)
            self.client.publish(address, val, retain = self.retain, qos = self.qos)
            a = a + 1