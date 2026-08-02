import os
import pytest

from pydag.agents.app.AgentApp import AgentApp
from pydag.services.csv.CsvWriteService import CsvWriteService
from pydag.buffers.ListBuffer import ListBuffer
from pydag.agents.Agent import Agent
try:    
    from pydag.services.ads.AdsService import AdsService
except (ImportError, OSError, FileNotFoundError) as exc:
    pytest.skip(f"ADS tests require pyads/TcAdsDll: {exc}", allow_module_level=True)



def test_000():
    aa : AgentApp = AgentApp()
    
    ag = Agent(id = "AG1")
    
    buf = ListBuffer(
        id = "B1",
        capacity = 1,
        data_type = "NUMERIC"
    )
    
    ag.add_buffer(buf)
    
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
    ag.add_service(ads)
    
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
    
    ag.add_service(csv)
    
    aa.set_agent(ag)
    
    aa.save(f"{os.path.dirname(__file__)}\\ads_csv.yaml")
    

def test_001():
    aa : AgentApp = AgentApp.load(f"{os.path.dirname(__file__)}\\ads_csv.yaml")
    print(aa.get_agent())