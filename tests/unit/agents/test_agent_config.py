import importlib
import os
import shutil
from pathlib import Path
import pytest
import yaml

from pydag.adapters.opcua.OpcUaAdapter import OpcUaAdapter
from pydag.buffers.ListBuffer import ListBuffer
from pydag.agents.AgentConfig import AgentConfig
from pydag.agents.YAMLConfig import YAMLConfig
from pydag.agents.Agent import Agent
from pydag.services.mappings.MappingService import MappingService
from pydag.services.ThreadType import ThreadType
from pydag.utils.ClassUtils import ClassUtils
from tests.unit.agents.ConfigObject import ConfigObject


def test_000():
    yaml_file = open(os.path.dirname(__file__) + "\\config.yaml", "r")
    d = yaml.safe_load(yaml_file)
    print(d)
    

@pytest.mark.skip(reason="not working")    
def test_010():
    module = __import__("pydag.adapters.opcua.OpcUaAdapter")
    clazz = getattr(module, "OpcUaAdapter")
    instance = clazz()
    print(instance.id)

def test_011():
    Clazz = getattr(importlib.import_module("pydag.adapters.opcua.OpcUaAdapter"), "OpcUaAdapter")
    instance = Clazz()
    print(instance.id)
    
def test_020():
    opc = OpcUaAdapter()
    print(opc)
    
def test_030():
    co = ConfigObject()
    print(co)
    
def test_040():
    g = Agent()
    g.id = "G1"
    
    a = OpcUaAdapter()
    a.id = "A1"
    a.endpoint = "opc.tcp://localhost:4840/freeopcua/server/"
    
    b = ListBuffer()
    b.id = "B1"
    b.capacity = 1000
    b.description = "Test buffer"
    
    m = MappingService()
    m.id = "M1"
    m.buffer_ids = [b.id]
    m.adapter_id = a.id
    
    g.add_adapter(a)
    g.add_buffer(b)
    g.add_service(m)
    
    gc = AgentConfig(g)
    print(gc)
    
def test_041():
    g = Agent()
    g.id = "G1"
    
    a = OpcUaAdapter()
    a.id = "A1"
    a.endpoint = "opc.tcp://localhost:4840/freeopcua/server/"
    
    b = ListBuffer()
    b.id = "B1"
    b.capacity = 1000
    b.description = "Test buffer"
    
    m = MappingService()
    m.id = "M1"
    m.buffer_ids = [b.id]
    m.adapter_id = a.id
    m.thread_type = ThreadType.MILLI_SECOND.value
    
    g.add_adapter(a)
    g.add_buffer(b)
    g.add_service(m)
    
    gc = AgentConfig(g)
    
    yc = YAMLConfig(os.path.dirname(__file__) + "\\agent_config1.yaml")
    
    yc.save(gc)
    
def test_042():
    yc = YAMLConfig(os.path.dirname(__file__) + "\\agent_config1.yaml")
    gc : AgentConfig = yc.load()
    print(gc)
    g = gc.create()
    gc2 = AgentConfig(g)
    print(gc2)

@pytest.mark.skip("test manually")
def test_043_yaml_save_bare_filename(monkeypatch):
    test_dir = Path(os.path.dirname(__file__)) / "tmp_yaml_save_bare"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    monkeypatch.chdir(test_dir)

    agent = Agent()
    agent.id = "G2"
    gc = AgentConfig(agent)
    yc = YAMLConfig("agent_config_bare.yaml")

    yc.save(gc)

    assert (test_dir / "agent_config_bare.yaml").is_file()

@pytest.mark.skip("test manually")
def test_044_agent_release_writes_default_yaml_to_cwd(monkeypatch):
    test_dir = Path(os.path.dirname(__file__)) / "tmp_agent_release_yaml"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    monkeypatch.chdir(test_dir)

    agent = Agent()
    agent.id = "ReleaseTest"

    agent.release(blocking=False)
    agent.terminate()

    assert (test_dir / "Agent ReleaseTest.yaml").is_file()
    
def test_050():
    
    print(AgentConfig.FEATURES)
    
    clazz = ClassUtils.create_class("pydag.agents.AgentConfig")
    
    print(type(clazz))
    
    
