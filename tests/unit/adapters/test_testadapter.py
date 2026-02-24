from tests.unit.adapters.Adapter1 import Adapter1

def test_000():
    adapter = Adapter1()
    adapter.id = "TEST"
    adapter.run()
    assert adapter.id == "TEST"