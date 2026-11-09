"""Live Codex test; requires an installed, authenticated CLI."""
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.llm.AgentHarnessAction import AgentHarnessAction


def test_live_codex_uses_parent_prompt(tmp_path):
    parent = LinkBufferAction()
    parent.install()
    action = AgentHarnessAction(
        prompt_key="task_prompt", output_keys=["harness_result"], working_directory=str(tmp_path),
    )
    action.add_parent(parent)
    action.install()
    action.execute()
    assert action.get_buffer().size() == 0
    parent.add_data({"task_prompt": "Reply with exactly harness-ok, without formatting. Do not use tools or change files."})
    action.execute()

    data = action.get_data()
    assert data["harness_result"][0].strip() == "harness-ok"
