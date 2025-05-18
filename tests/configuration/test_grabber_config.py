import importlib
import os
import yaml

from PyDataGrabber.src.adapters.opcua.OpcUaAdapter import OpcUaAdapter
from PyDataGrabber.tests.configuration.ConfigObject import ConfigObject


def test_000():
    yaml_file = open(os.path.dirname(__file__) + "\\config.yaml", "r")
    d = yaml.safe_load(yaml_file)
    print(d)
    
def test_010():
    module = __import__("PyDataGrabber.src.adapters.opcua")
    clazz = getattr(module, "OpcUaAdapter")
    instance = clazz()
    print(instance.id)

def test_011():
    Clazz = getattr(importlib.import_module("PyDataGrabber.src.adapters.opcua.OpcUaAdapter"), "OpcUaAdapter")
    instance = Clazz()
    print(instance.id)
    
def test_020():
    opc = OpcUaAdapter()
    print(opc)
    
def test_030():
    co = ConfigObject()
    print(co)