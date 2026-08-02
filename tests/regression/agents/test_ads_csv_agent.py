import os
import pytest

from pydag.services.csv.CsvWriteService import CsvWriteService
from pydag.buffers.ListBuffer import ListBuffer
from pydag.agents.AgentKeywords import AgentKeywords
from pydag.agents.YAMLConfig import YAMLConfig
from pydag.agents.Agent import Agent
try:    
    from pydag.services.ads.AdsService import AdsService
except (ImportError, OSError, FileNotFoundError) as exc:
    pytest.skip(f"ADS tests require pyads/TcAdsDll: {exc}", allow_module_level=True)



def test_000():
    g = Agent(id = "AG1")
    
    buf = ListBuffer(
        id = "B1",
        capacity = 1,
        data_type = "NUMERIC"
    )
    
    g.add_buffer(buf)
    
    ads = AdsService(
        id = "A1",
        ams_net_id = "191.1.1.1.1.1",
        buffer_ids = [buf.id],
        addresses = ["MAIN.AdsCsvGrabberTest"],
        thread_type = "MILLI_SECOND",
        mapping_type = "READ",
        n = 1,
        observing_time = 10
    )
    g.add_service(ads)
    
    csv = CsvWriteService(
        id = "A2",
        folder = os.path.dirname(__file__),
        decimal_precision = 3,
        delimiter = ";",
        file_extension = "csv",
        max_samples = 1000000,
        file_post_fix = "125kN",
        buffer_ids = [buf.id],
        mapping_type = "WRITE",
        persistent = False,
        observing_time = 10,
        thread_type = "MILLI_SECOND"
    )
    
    g.add_service(csv)
    
    gc = AgentKeywords(g)
    yc = YAMLConfig(os.path.dirname(__file__) + "\\ads_csv.yaml")
    yc.save(gc)

def test_001():
    yc = YAMLConfig(os.path.dirname(__file__) + "\\ads_csv.yaml")
    gc = yc.load()
    print(gc)