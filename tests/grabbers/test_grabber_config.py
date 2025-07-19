import importlib
import os
import yaml

from pydg.adapters.opcua.OpcUaAdapter import OpcUaAdapter
from pydg.buffers.ListBuffer import ListBuffer
from pydg.grabbers.GrabberConfig import GrabberConfig
from pydg.grabbers.YAMLConfig import YAMLConfig
from pydg.grabbers.Grabber import Grabber
from pydg.mappings.Mapping import Mapping
from pydg.mappings.ThreadType import ThreadType
from tests.grabbers.ConfigObject import ConfigObject


def test_000():
    yaml_file = open(os.path.dirname(__file__) + "\\config.yaml", "r")
    d = yaml.safe_load(yaml_file)
    print(d)
    
def test_010():
    module = __import__("pydatagrabber.adapters.opcua")
    clazz = getattr(module, "OpcUaAdapter")
    instance = clazz()
    print(instance.id)

def test_011():
    Clazz = getattr(importlib.import_module("pydatagrabber.adapters.opcua.OpcUaAdapter"), "OpcUaAdapter")
    instance = Clazz()
    print(instance.id)
    
def test_020():
    opc = OpcUaAdapter()
    print(opc)
    
def test_030():
    co = ConfigObject()
    print(co)
    
def test_040():
    g = Grabber()
    g.id = "G1"
    
    a = OpcUaAdapter()
    a.id = "A1"
    a.endpoint = "opc.tcp://localhost:4840/freeopcua/server/"
    
    b = ListBuffer()
    b.id = "B1"
    b.capacity = 1000
    b.description = "Test buffer"
    
    m = Mapping()
    m.id = "M1"
    m.buffer_ids = [b.id]
    m.adapter_id = a.id
    
    g.add_adapter(a)
    g.add_buffer(b)
    g.add_mapping(m)
    
    gc = GrabberConfig(g)
    print(gc)
    
def test_041():
    g = Grabber()
    g.id = "G1"
    
    a = OpcUaAdapter()
    a.id = "A1"
    a.endpoint = "opc.tcp://localhost:4840/freeopcua/server/"
    
    b = ListBuffer()
    b.id = "B1"
    b.capacity = 1000
    b.description = "Test buffer"
    
    m = Mapping()
    m.id = "M1"
    m.buffer_ids = [b.id]
    m.adapter_id = a.id
    m.thread_type = ThreadType.MILLI_SECOND.value
    
    g.add_adapter(a)
    g.add_buffer(b)
    g.add_mapping(m)
    
    gc = GrabberConfig(g)
    
    yc = YAMLConfig(os.path.dirname(__file__) + "\\grabber_config1.yaml")
    
    yc.save(gc)
    
def test042():
    yc = YAMLConfig(os.path.dirname(__file__) + "\\grabber_config1.yaml")
    gc = yc.load()
    print(gc)
    g = gc.create()
    gc2 = GrabberConfig(g)
    print(gc2)
    
    