from pydag.agents.Agent import Agent
from pydag.buffers.DatasetBuffer import DatasetBuffer


def test_000():
    ag = Agent(with_api=True, port=8008)
    
    buf1 = DatasetBuffer(id="DATASET_BUF_1", dataset_name="ArrowHead", duplicate_ids = ["DATASET_BUF_2", "DATASET_BUF_3"], index_enabled=True)
    buf1.install(ag)
    ag.add_buffer(buf1)
    
    ag.release()
    
    