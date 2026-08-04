from __future__ import annotations

import time
import multiprocessing
import os


from pydag.agents.AgentKeywords import AgentKeywords
from pydag.agents.app.AgentApp import AgentApp


def _run_agent(app_config: dict) -> None:
    agent_app : AgentApp = AgentApp.load(app_config)
    agent_app.create()
    agent_app.run()

class AgentProcessStore:
    def __init__(self) -> None:
        self._agent_configs: dict[str, dict] = {}
        self._processes: dict[str, multiprocessing.Process] = {}

    def add_app_template(self, id : str, agent_config: dict):
        #cloned_agent = copy.deepcopy(agent)
        self._agent_configs[id] = agent_config
        return agent_config

    def get_agent_config(self, agent_id: str) -> dict | None:
        return self._agent_configs.get(agent_id)

    def start_agent(self, agent_id: str) -> multiprocessing.Process:
        if agent_id not in self._agent_configs:
            raise KeyError(f"No agent with id={agent_id} was registered")

        existing_process = self._processes.get(agent_id)
        if existing_process is not None and existing_process.is_alive():
            return existing_process

        agent_copy = self._agent_configs[agent_id]
        context = multiprocessing.get_context("spawn")
        process = context.Process(target=_run_agent, args=(agent_copy,), daemon=True)
        process.start()
        self._processes[agent_id] = process
        return process

    def stop_agent(self, agent_id: str) -> None:
        process = self._processes.get(agent_id)
        if process is None:
            return

        if process.is_alive():
            process.terminate()
            process.join(timeout=5)

        self._processes.pop(agent_id, None)


def test_agent_process_store_can_start_and_stop_agents():
    aa1 : AgentApp = AgentApp.load(os.path.dirname(__file__) + os.sep + "sine_buffer_agent_app_template.yaml")
    aa2 : AgentApp = AgentApp.load(os.path.dirname(__file__) + os.sep + "bool_buffer_agent_app_template.yaml")

    store = AgentProcessStore()
    
    agent_config1 = aa1.config_options()
    agent_id1 = agent_config1[AgentKeywords.AGENT][AgentKeywords.ID]
    store.add_app_template(agent_id1, agent_config1)
    
    agent_config2 = aa2.config_options()
    agent_id2 = agent_config2[AgentKeywords.AGENT][AgentKeywords.ID]
    store.add_app_template(agent_id2, agent_config2)
    
    process1 = store.start_agent(agent_id1)
    process2 = store.start_agent(agent_id2)

    assert process1.is_alive()
    assert process2.is_alive()

    time.sleep(240)
    
    store.stop_agent(agent_id1)
    store.stop_agent(agent_id2)

    assert not process1.is_alive()
    assert not process2.is_alive()
