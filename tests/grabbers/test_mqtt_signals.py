        
from pydatagrabber.adapters.mqtt.MQTTAdapter import MQTTAdapter
from pydatagrabber.buffers.SignalBuffer import SignalBuffer
from pydatagrabber.buffers.signals.LinearTrend import LinearTrend
from pydatagrabber.buffers.signals.Sine import Sine
from pydatagrabber.grabbers.Grabber import Grabber
from pydatagrabber.mappings.Mapping import Mapping
from pydatagrabber.mappings.MappingType import MappingType
from pydatagrabber.mappings.ThreadType import ThreadType


def test_000():
    g = Grabber()
    g.id = "G-MQTT-1"

    s = Sine()
    s.f = 0.01
    s.a = 1.0
    s.p = 0.0
    s.n = 0.1
    sine_buf = SignalBuffer()
    sine_buf.id = "SINE-BUF"
    sine_buf.signal = s
    sine_buf.capacity=100
    sine_buf.sampling_period=10

    g.add_buffer(sine_buf)

    lt = LinearTrend()
    lt.min = 0.0
    lt.max = 100.0
    lt.duration = 60.0

    linear_buf = SignalBuffer()
    linear_buf.id = "LINEAR-BUF"
    linear_buf.signal = lt
    linear_buf.capacity = 1
    linear_buf.sampling_period = 1000

    g.add_buffer(linear_buf)

    mqtt_adapter = MQTTAdapter()
    mqtt_adapter.id = "MQTT-1"
    mqtt_adapter.endpoint  = "localhost"
    mqtt_adapter.port = 1883
    mqtt_adapter.qos = 1
    mqtt_adapter.force_numeric = True
    
    g.add_adapter(mqtt_adapter)

    m1 = Mapping()
    m1.id = "M1"
    m1.adapter = mqtt_adapter
    m1.addresses = ["signals/sine", "signals/linear"]
    m1.buffers = {sine_buf.id : sine_buf, linear_buf.id: linear_buf}
    m1.thread_type = ThreadType.MILLI_SECOND.value
    m1.mapping_type = MappingType.WRITE.value
    m1.sampling_period = 1000
    m1.n = 0

    g.add_mapping(m1)

    g.start_blocking()

    
    