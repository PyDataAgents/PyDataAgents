from pydag.agents.Agent import Agent
from pydag.agents.app.AgentApp import AgentApp
from pydag.buffers.DatasetBuffer import DatasetBuffer


def test_000():
    ag = Agent()
    buf1 = DatasetBuffer(id="DATASET_BUF_1", dataset_name="ArrowHead", duplicate_ids = ["DATASET_BUF_2", "DATASET_BUF_3"], index_enabled=True)
    buf1.install(ag)
    ag.add_buffer(buf1)
    
    app = AgentApp(with_api=True)
    app.set_agent(ag)
    app.create()
    app.run()
    
    