from pydag.nodes.DataElementConfig import DataElementConfig
from pydag.utils.ClassUtils import ClassUtils

def test_000():
    
    print(DataElementConfig.FEATURES)
    
    clazz = ClassUtils.create_class("pydag.nodes.DataElementConfig")
    
    print(type(clazz))