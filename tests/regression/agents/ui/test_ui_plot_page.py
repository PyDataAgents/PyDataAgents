from pydag.agents.Agent import Agent
from pydag.agents.app.AgentApp import AgentApp
from pydag.agents.ui.UIPlotPage import UIPlotPage
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.RandBoolean import RandBoolean
from pydag.buffers.signals.Sine import Sine


def test_agent_app_plot_page_refreshes_from_multiple_changing_buffers():
    agent = Agent()
    rand_buffer = SignalBuffer(
        signal=RandBoolean(),
        id="rand"
    )
    value_buffer = SignalBuffer(
        signal=Sine()
    )
    agent.add_buffer(rand_buffer)
    agent.add_buffer(value_buffer)

    page = UIPlotPage(samples=100)

    app = AgentApp(with_ui=True, agent=agent, ui_pages=[page])
    app.create()
    app.run()
