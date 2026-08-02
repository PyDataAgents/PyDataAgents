from __future__ import annotations

import multiprocessing

from pydag.agents.Agent import Agent
from pydag.agents.AgentKeywords import AgentKeywords
from pydag.agents.app import AgentApp


def _run_agent(agent_config: AgentKeywords) -> None:
    agent : Agent = agent_config.create()
    agent.release(blocking=True)

class AgentProcessStore:
    def __init__(self) -> None:
        self._agent_configs: dict[str, AgentKeywords] = {}
        self._processes: dict[str, multiprocessing.Process] = {}

    def add_app_template(self, agent_config: AgentKeywords) -> AgentKeywords:
        #cloned_agent = copy.deepcopy(agent)
        self._agent_configs[agent_config.to_dict()[AgentKeywords.ID]] = agent_config
        return agent_config

    def get_agent_config(self, agent_id: str) -> AgentKeywords | None:
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
    aa : AgentApp = AgentApp(agent=Agent(id="A1"))
    store = AgentProcessStore()

    stored_agent = store.add_agent(agent_config)
    process = store.start_agent(stored_agent.to_dict()[AgentKeywords.ID])

    assert process.is_alive()

    store.stop_agent(stored_agent.to_dict()[AgentKeywords.ID])

    assert not process.is_alive()
