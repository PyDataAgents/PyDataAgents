import subprocess
from contextlib import nullcontext
from unittest.mock import MagicMock

import pytest

from pydag.agents.AgentElementException import AgentElementException
from pydag.nodes.NodeException import NodeException
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.llm.AgentHarnessAction import AgentHarnessAction


@pytest.fixture(autouse=True)
def popen(monkeypatch):
    """Keep every test independent of an installed/authenticated harness."""
    monkeypatch.setattr("pydag.nodes.llm.AgentHarnessAction.shutil.which", lambda _: "C:/Program Files/Codex/codex.cmd")
    mock = MagicMock()
    process = mock.return_value
    process.__enter__.return_value = process
    process.communicate.return_value = ("final answer\n", "diagnostic\n")
    process.returncode = 0
    monkeypatch.setattr("pydag.nodes.llm.AgentHarnessAction.subprocess.Popen", mock)
    return mock


@pytest.fixture
def action(tmp_path):
    return AgentHarnessAction(prompt="literal task", working_directory=str(tmp_path))


def _parent(rows):
    parent = LinkBufferAction()
    parent.install()
    parent.add_data(rows)
    return parent


@pytest.mark.parametrize("output_keys", [[], ["stdout"], ["harness_result"]])
def test_literal_prompt_runs_once_and_captures_output(action, popen, output_keys):
    action.output_keys = output_keys
    parent = _parent([{"task_prompt": "first"}, {"task_prompt": "second"}])
    action.add_parent(parent)
    action.persistent = False
    action.install()
    action.execute()

    popen.assert_called_once_with(
        ["C:/Program Files/Codex/codex.cmd", "exec", "--skip-git-repo-check", "--sandbox", "workspace-write", "literal task"],
        cwd=action.working_directory, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
    )
    data = action.get_data()
    assert data[output_keys[0] if output_keys else "stdout"] == ["final answer\n"]
    assert data["stderr"] == ["diagnostic\n"]
    assert data["exit_code"] == [0]
    assert parent.get_buffer().size() == 2


@pytest.mark.parametrize("persistent", [True, False])
@pytest.mark.parametrize("n", [0, 2])
def test_prompt_key_runs_per_selected_row(action, popen, persistent, n):
    prompts = ["first", "second", "third"]
    parent = _parent([{"task_prompt": value, "other": "ignored"} for value in prompts])
    action.add_parent(parent)
    action.prompt, action.prompt_key = None, "task_prompt"
    action.input_keys = ["task_prompt"]
    action.output_keys = ["harness_result"]
    action.n, action.persistent = n, persistent
    selected = prompts[:n or None]
    output_pairs = [(f"{prompt} answer\n", f"{prompt} diagnostic\n") for prompt in selected]
    popen.return_value.communicate.side_effect = output_pairs
    action.install()
    action.execute()

    assert [call.args[0][-1] for call in popen.call_args_list] == selected
    data = action.get_data()
    assert data["harness_result"] == [stdout for stdout, _ in output_pairs]
    assert data["stderr"] == [stderr for _, stderr in output_pairs]
    assert data["exit_code"] == [0] * len(selected)
    assert "stdout" not in data
    assert parent.get_data()["task_prompt"] == (prompts if persistent else prompts[len(selected):])


@pytest.mark.parametrize("settings, message", [
    ({"prompt": None}, "exactly one"),
    ({"prompt_key": "task_prompt"}, "exactly one"),
    ({"prompt": ""}, "prompt must be"),
    ({"prompt": " \n"}, "prompt must be"),
    ({"prompt": 42}, "prompt must be"),
    ({"prompt": None, "prompt_key": " "}, "prompt_key must be"),
    ({"prompt": None, "prompt_key": 42}, "prompt_key must be"),
    ({"output_keys": ["a", "b"]}, "output_keys must be"),
    ({"output_keys": "result"}, "output_keys must be"),
    ({"output_keys": None}, "output_keys must be"),
    ({"output_keys": [""]}, "stdout destination"),
    ({"output_keys": [" "]}, "stdout destination"),
    ({"output_keys": [42]}, "stdout destination"),
    ({"output_keys": ["stderr"]}, "stdout destination"),
    ({"output_keys": ["exit_code"]}, "stdout destination"),
    ({"harness": "unknown"}, "Unsupported harness"),
    ({"working_directory": None}, "existing directory"),
])
def test_install_rejects_invalid_configuration(action, popen, settings, message):
    for name, value in settings.items():
        setattr(action, name, value)
    with pytest.raises(AgentElementException, match=message) as error:
        action.install()
    assert isinstance(error.value.__cause__, NodeException)
    popen.assert_not_called()


def test_install_requires_harness_on_path(action, monkeypatch):
    monkeypatch.setattr("pydag.nodes.llm.AgentHarnessAction.shutil.which", lambda _: None)
    with pytest.raises(AgentElementException, match="installed and executable on PATH"):
        action.install()


@pytest.mark.parametrize("is_file", [False, True])
def test_install_requires_existing_directory(action, tmp_path, is_file):
    path = tmp_path / "workspace"
    if is_file:
        path.write_text("not a directory", encoding="utf-8")
    action.working_directory = str(path)
    with pytest.raises(AgentElementException, match="existing directory"):
        action.install()


def test_install_requires_accessible_directory(action, monkeypatch):
    monkeypatch.setattr("pydag.nodes.llm.AgentHarnessAction.os.access", lambda *_: False)
    with pytest.raises(AgentElementException, match="must be accessible"):
        action.install()


@pytest.mark.parametrize("rows, input_keys, ignore_empty_parents, message", [
    (None, [], True, "No parent"),
    ([], [], True, None),
    ([], [], False, "No data was found"),
    ([{"other": "value"}], [], True, "Missing configured prompt_key"),
    ([{"task_prompt": "valid", "other": "value"}], ["other"], True, "Missing configured prompt_key"),
    ([{"task_prompt": "valid"}, {"task_prompt": ""}], [], True, "prompt must be"),
    ([{"task_prompt": " \n"}], [], True, "prompt must be"),
    ([{"task_prompt": None}], [], True, "prompt must be"),
    ([{"task_prompt": 42}], [], True, "prompt must be"),
])
def test_parent_input_validation_does_not_launch_harness(action, popen, rows, input_keys, ignore_empty_parents, message):
    action.prompt, action.prompt_key = None, "task_prompt"
    action.input_keys = input_keys
    action.ignore_empty_parents = ignore_empty_parents
    if rows is not None:
        action.add_parent(_parent(rows))
    action.install()
    with pytest.raises(NodeException, match=message) if message else nullcontext():
        action.execute()
    popen.assert_not_called()
    assert action.get_buffer().size() == 0





def test_launch_failure_has_clear_error(action, popen):
    action.install()
    popen.side_effect = FileNotFoundError("executable disappeared")
    with pytest.raises(NodeException, match="Could not execute harness 'codex'"):
        action.execute()
    assert action.get_buffer().size() == 0
