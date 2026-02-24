import os
import pytest

try:
    from pydag.adapters.ads.AdsAdapter import AdsAdapter
except (ImportError, OSError, FileNotFoundError) as exc:
    pytest.skip(f"ADS tests require pyads/TcAdsDll: {exc}", allow_module_level=True)

from pydag.adapters.csv.CsvWriteAdapter import CsvWriteAdapter
from pydag.buffers.ListBuffer import ListBuffer
from pydag.agents.AgentConfig import AgentConfig
from pydag.agents.YAMLConfig import YAMLConfig
from pydag.agents.Agent import Agent
from pydag.services.mappings.MappingService import MappingService


def test_000():
    g = Agent()
    g.id = "AG1"
    
    ads = AdsAdapter()
    ads.id = "A1"
    ads.ams_net_id = "191.1.1.1.1.1"
    
    csv = CsvWriteAdapter()
    csv.id = "A2"
    csv.folder = os.path.dirname(__file__)
    csv.decimal_precision = 3
    csv.delimiter = ";"
    csv.file_extension = "csv"
    csv.max_samples = 1000000
    csv.file_post_fix = "125kN"
    
    buf = ListBuffer()
    buf.id = "B1"
    buf.capacity = 1
    buf.data_type = "NUMERIC"
    
    m1 = MappingService()
    m1.id = "M1"
    m1.buffer_ids = [buf.id]
    m1.adapter_id = ads.id
    m1.addresses = ["MAIN.AdsCsvGrabberTest"]
    m1.thread_type = "MILLI_SECOND"
    m1.mapping_type = "READ"
    m1.n = 1
    m1.observing_time = 10
    
    m2 = MappingService()
    m2.id = "M2"
    m2.buffer_ids = [buf.id]
    m2.adapter_id = csv.id
    m2.mapping_type = "WRITE"
    m2.persistent = False
    m2.observing_time = 10
    m2.thread_type = "MILLI_SECOND"
    
    g.add_adapter(ads)
    g.add_adapter(csv)
    g.add_buffer(buf)
    g.add_service(m1)
    g.add_service(m2)
    
    gc = AgentConfig(g)
    yc = YAMLConfig(os.path.dirname(__file__) + "\\ads_csv.yaml")
    yc.save(gc)

def test_001():
    yc = YAMLConfig(os.path.dirname(__file__) + "\\ads_csv.yaml")
    gc = yc.load()
    print(gc)