from dataclasses import dataclass, field

from pydag.agents.AgentElement import AgentElement
from pydag.services.Service import Service
from pydag.services.csv.CsvReadService import CsvReadService
from pydag.services.datamodel.DataModel import DataModel
from pydag.utils.ClassUtils import ClassUtils

@dataclass
class TestDataClass1():
    name : str = field(default="", metadata={"description": "The name of the person"})
    age : int = field(default=0, metadata={"description": "The age of the person"})

@dataclass
class TestDataClass2():
    c : TestDataClass1 = field(default_factory=TestDataClass1, metadata={"description": "A nested data class"})
    p : int = 100

def test_000():
    #ge = GrabberElement()
    
    fields = ClassUtils.get_dataclass_fields(AgentElement)
    print(fields)
    
    
def test_020():
    print(ClassUtils.get_superclasses(CsvReadService))
    
def test_030():
    print(ClassUtils.get_subclasses(Service))
    
    
def test_040():
    res = ClassUtils.find_subclasses(DataModel, "tests\\unit\\services\\datamodel")
    print(res)
    
def test_041():
    res = ClassUtils.find_subclasses(Service, "pydag\\services")
    print(res)
    
def test_config_options():
    tdc = TestDataClass1(name="John", age=30)
    options = ClassUtils.config_options(tdc, with_descriptions=False)
    print(options)
    assert len(options) == 2
    
def test_config_options_with_descriptions():
    tdc = TestDataClass1(name="John", age=30)
    options = ClassUtils.config_options(tdc, with_descriptions=True)
    print(options)
    assert len(options) == 2
    
def test_config_options_with_nesting():
    tdc2 = TestDataClass2(c=TestDataClass1(name="Alice", age=25), p=200)
    options = ClassUtils.config_options(tdc2, with_descriptions=False)
    print(options)
    assert len(options) == 2
    
def test_config_options_with_nesting_and_descriptions():
    tdc2 = TestDataClass2(c=TestDataClass1(name="Alice", age=25), p=200)
    options = ClassUtils.config_options(tdc2, with_descriptions=True)
    print(options)
    assert len(options) == 2
    
def test_set_object_properties():
    tdc = TestDataClass1()
    properties = {"name": "Bob", "age": 40}
    ClassUtils.set_properties(tdc, properties)
    assert tdc.name == "Bob"
    assert tdc.age == 40
    
def test_create_class_instance():
    tdc = ClassUtils.create_instance("tests.unit.utils.test_classutils.TestDataClass1")
    properties = {"name": "Bob", "age": 40}
    ClassUtils.set_properties(tdc, properties)
    assert tdc.name == "Bob"
    assert tdc.age == 40
    
def test_create_class_instance_with_nested():
    tdc2 = ClassUtils.create_instance("tests.unit.utils.test_classutils.TestDataClass2")
    properties = {"c": {"name": "Charlie", "age": 50}, "p": 300}
    ClassUtils.set_properties(tdc2, properties)
    assert tdc2.c.name == "Charlie"
    assert tdc2.c.age == 50
    assert tdc2.p == 300
    
def test_create_class_instance_with_nested_from_type():
    tdc2 = ClassUtils.create_instance("tests.unit.utils.test_classutils.TestDataClass2")
    properties = {"c": {"type": "tests.unit.utils.test_classutils.TestDataClass1", "name": "Charlie", "age": 50}, "p": 300}
    ClassUtils.set_properties(tdc2, properties)
    assert tdc2.c.name == "Charlie"
    assert tdc2.c.age == 50
    assert tdc2.p == 300