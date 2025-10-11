from pydag_de.DataElementConfig import DataElementConfig
from pydag.utils.ClassUtils import ClassUtils

def test_000():
    
    print(DataElementConfig.FEATURES)
    
    clazz = ClassUtils.create_class("pydag_de.DataElementConfig")
    
    print(type(clazz))