        
from pydag.services.mqtt.MQTTService import MQTTService
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.LinearTrend import LinearTrend
from pydag.buffers.signals.Sine import Sine
from pydag.agents.Agent import Agent
from pydag.services.MappingType import MappingType
from pydag.services.ThreadType import ThreadType


def test_000():
    ag = Agent()
    ag.id = "AG-MQTT-1"

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

    ag.add_buffer(sine_buf)

    lt = LinearTrend()
    lt.min = 0.0
    lt.max = 100.0
    lt.duration = 60.0

    linear_buf = SignalBuffer()
    linear_buf.id = "LINEAR-BUF"
    linear_buf.signal = lt
    linear_buf.capacity = 1
    linear_buf.sampling_period = 1000

    ag.add_buffer(linear_buf)

    mqtt_srv = MQTTService(
        id = "MQTT-1",
        endpoint  = "localhost",
        port = 1883,
        qos = 1,
        force_numeric = True,
        addresses = ["signals/sine", "signals/linear"],
        thread_type = ThreadType.MILLI_SECOND.value,
        mapping_type = MappingType.WRITE.value,
        observing_time = 1000,
        n = 0,
        persistent = False,
        auto_start = True
    )
    mqtt_srv.add_buffer(sine_buf)
    mqtt_srv.add_buffer(linear_buf)
    
    ag.add_service(mqtt_srv)

    ag.release()

    
    