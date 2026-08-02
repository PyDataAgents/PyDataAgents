import importlib
import os
import shutil
from pathlib import Path
import pytest
import yaml

from pydag.services.opcua.OpcUaService import OpcUaService
from pydag.buffers.ListBuffer import ListBuffer
from pydag.agents.AgentKeywords import AgentKeywords
from pydag.agents.YAMLConfig import YAMLConfig
from pydag.agents.Agent import Agent
from pydag.services.ThreadType import ThreadType
from pydag.utils.ClassUtils import ClassUtils
from tests.unit.agents.ConfigObject import ConfigObject


def test_000():
    yaml_file = open(os.path.dirname(__file__) + "\\config.yaml", "r", encoding="utf-8")
    d = yaml.safe_load(yaml_file)
    print(d)
    

@pytest.mark.skip(reason="not working")    
def test_010():
    module = __import__("pydag.services.opcua.OpcUaService")
    clazz = getattr(module, "OpcUaService")
    instance = clazz()
    print(instance.id)

def test_011():
    Clazz = getattr(importlib.import_module("pydag.services.opcua.OpcUaService"), "OpcUaService")
    instance = Clazz()
    print(instance.id)
    
def test_020():
    opc = OpcUaService()
    print(opc)
    
def test_030():
    co = ConfigObject()
    print(co)
    
def test_040():
    g = Agent()
    g.id = "G1"
    
    b = ListBuffer()
    b.id = "B1"
    b.capacity = 1000
    b.description = "Test buffer"
    
    a = OpcUaService()
    a.id = "A1"
    a.endpoint = "opc.tcp://localhost:4840/freeopcua/server/"
    a.add_buffer(b)
    
    g.add_buffer(b)
    g.add_service(a)
    
    gc = AgentKeywords(g)
    print(gc)
    
def test_041():
    g = Agent()
    g.id = "G1"
    
    b = ListBuffer()
    b.id = "B1"
    b.capacity = 1000
    b.description = "Test buffer"
    
    g.add_buffer(b)
    
    a = OpcUaService()
    a.id = "A1"
    a.endpoint = "opc.tcp://localhost:4840/freeopcua/server/"
    a.thread_type = ThreadType.MILLI_SECOND.value
    a.add_buffer(b)
        
    g.add_service(a)
    
    gc = AgentKeywords(g)
    
    yc = YAMLConfig(os.path.dirname(__file__) + "\\agent_config1.yaml")
    
    yc.save(gc)
    
def test_042():
    yc = YAMLConfig(os.path.dirname(__file__) + "\\agent_config1.yaml")
    gc : AgentKeywords = yc.load()
    print(gc)
    g = gc.create()
    gc2 = AgentKeywords(g)
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
    gc = AgentKeywords(agent)
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
    
    print(AgentKeywords.FEATURES)
    
    clazz = ClassUtils.create_class("pydag.agents.AgentKeywords")
    
    print(type(clazz))
    
    
