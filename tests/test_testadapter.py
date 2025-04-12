from PyDataGrabber.pydatagrabber.adapter1 import Adapter1

def test_000():
    adapter = Adapter1().set_id("TEST")
    adapter.run()
    assert adapter.get_id() == "TEST"