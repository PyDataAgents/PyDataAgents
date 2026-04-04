from tests.unit.agents.SimpleAgentElement import SimpleAgentElement

def test_000():
    a = SimpleAgentElement()    
    print(a.id)
    
def test_010():
    a = SimpleAgentElement(id="A1")
    print(a.id)
    assert a.id == "A1", "ID should be set to 'A1'"