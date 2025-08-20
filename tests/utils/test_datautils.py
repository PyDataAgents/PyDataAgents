from pydag.utils.DataUtils import DataUtils


class TestClass1:    
    def __init__(self):
        self.a = 10
        self.b = 'a'
        self.c = TestClass2()
        
class TestClass2:    
    def __init__(self):
        self.d = 'Joe'
        self.e = 10.1

def test_000():
    
    tc = TestClass1()
    print(DataUtils.obj_to_dict(tc))
    