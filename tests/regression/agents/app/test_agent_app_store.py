from __future__ import annotations

import copy
import multiprocessing

from pydag.agents.Agent import Agent


def _run_agent(agent: Agent) -> None:
    agent.release(blocking=True)

class AgentProcessStore:
    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}
        self._processes: dict[str, multiprocessing.Process] = {}

    def add_agent(self, agent: Agent) -> Agent:
        cloned_agent = copy.deepcopy(agent)
        self._agents[cloned_agent.id] = cloned_agent
        return cloned_agent

    def get_agent(self, agent_id: str) -> Agent | None:
        return self._agents.get(agent_id)

    def start_agent(self, agent_id: str) -> multiprocessing.Process:
        if agent_id not in self._agents:
            raise KeyError(f"No agent with id={agent_id} was registered")

        existing_process = self._processes.get(agent_id)
        if existing_process is not None and existing_process.is_alive():
            return existing_process

        agent_copy = copy.deepcopy(self._agents[agent_id])
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
    agent = Agent(id="test-store-agent", with_ui=False, with_api=False)
    store = AgentProcessStore()

    stored_agent = store.add_agent(agent)
    process = store.start_agent(stored_agent.id)

    assert process.is_alive()

    store.stop_agent(stored_agent.id)

    process.join(timeout=5)
    assert not process.is_alive()
