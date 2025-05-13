from PyDataGrabber.tests.adapters.Adapter1 import Adapter1

def test_000():
    adapter = Adapter1("TEST")
    adapter.run()
    assert adapter.id == "TEST"