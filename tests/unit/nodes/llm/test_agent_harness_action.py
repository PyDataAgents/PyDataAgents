import subprocess
import sys
from contextlib import nullcontext
from unittest.mock import MagicMock

import pytest

from pydag.agents.AgentElementException import AgentElementException
from pydag.nodes.NodeException import NodeException
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.llm.AgentHarnessAction import AgentHarnessAction


REAL_POPEN = subprocess.Popen


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


@pytest.mark.parametrize("output_keys", [[], ["harness_result"]])
def test_literal_prompt_runs_once_and_captures_output(action, popen, output_keys):
    action.output_keys = output_keys
    parent = _parent([{"task_prompt": "first"}, {"task_prompt": "second"}])
    action.add_parent(parent)
    action.persistent = False
    action.install()
    action.execute()

    popen.assert_called_once_with(
        ["C:/Program Files/Codex/codex.cmd", "exec", "--skip-git-repo-check", "--sandbox", "workspace-write", "-"],
        cwd=action.working_directory, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", bufsize=1,
    )
    popen.return_value.communicate.assert_called_once_with(input="literal task")
    data = action.get_data()
    assert data[output_keys[0] if output_keys else "stdout"] == ["final answer\n"]
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

    assert [call.kwargs["input"] for call in popen.return_value.communicate.call_args_list] == selected
    data = action.get_data()
    assert data["harness_result"] == [stdout for stdout, _ in output_pairs]
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
    ({"instruction": "rules", "instruction_key": "rules"}, "either instruction or instruction_key"),
    ({"instruction": None}, "instruction must be"),
    ({"instruction": 42}, "instruction must be"),
    ({"instruction_key": ""}, "instruction_key must be"),
    ({"instruction_key": " "}, "instruction_key must be"),
    ({"instruction_key": 42}, "instruction_key must be"),
    ({"output_keys": ["a", "b"]}, "output_keys must be"),
    ({"output_keys": "result"}, "output_keys must be"),
    ({"output_keys": None}, "output_keys must be"),
    ({"output_keys": [""]}, "stdout destination"),
    ({"output_keys": [" "]}, "stdout destination"),
    ({"output_keys": [42]}, "stdout destination"),
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


@pytest.mark.parametrize("instruction", ["", "Answer in JSON.\nBe concise."])
@pytest.mark.parametrize("keyed_prompt", [False, True])
def test_literal_instruction(action, popen, instruction, keyed_prompt):
    action.instruction = instruction
    prompts = ["first", "second"] if keyed_prompt else [action.prompt]
    if keyed_prompt:
        action.prompt, action.prompt_key = None, "task"
        action.add_parent(_parent([{"task": prompt} for prompt in prompts]))
    action.install()
    action.execute()

    assert [call.kwargs["input"] for call in popen.return_value.communicate.call_args_list] == [
        f"Instruction:\n{instruction}\n\nPrompt:\n{prompt}" if instruction else prompt
        for prompt in prompts
    ]


@pytest.mark.parametrize("keyed_prompt", [False, True])
@pytest.mark.parametrize("persistent", [False, True])
@pytest.mark.parametrize("n", [0, 2])
def test_instruction_key_uses_same_selected_rows(action, popen, keyed_prompt, persistent, n):
    rows = [
        {"task": "first", "rules": "Be concise."},
        {"task": "second", "rules": ""},
        {"task": "third", "rules": "Answer in JSON."},
    ]
    parent = _parent(rows)
    action.add_parent(parent)
    action.instruction_key = "rules"
    action.input_keys = ["task", "rules"]
    action.n, action.persistent = n, persistent
    if keyed_prompt:
        action.prompt, action.prompt_key = None, "task"
    action.install()
    action.execute()

    expected = []
    for row in rows[:n or None]:
        prompt = row["task"] if keyed_prompt else action.prompt
        expected.append(f"Instruction:\n{row['rules']}\n\nPrompt:\n{prompt}" if row["rules"] else prompt)
    assert [call.kwargs["input"] for call in popen.return_value.communicate.call_args_list] == expected
    assert action.get_data()["stdout"] == ["final answer\n"] * len(expected)
    assert parent.get_buffer().size() == (len(rows) if persistent else len(rows) - len(expected))


@pytest.mark.parametrize("rows, input_keys, message", [
    (None, [], "No parent"),
    ([], [], None),
    ([{"other": "value"}], [], "Missing configured instruction_key"),
    ([{"rules": "valid", "other": "value"}], ["other"], "Missing configured instruction_key"),
    ([{"rules": "valid"}, {"rules": 42}], [], "instruction must be"),
    ([{"rules": None}], [], "instruction must be"),
])
def test_invalid_instruction_rows_do_not_launch_harness(action, popen, rows, input_keys, message):
    action.instruction_key = "rules"
    action.input_keys = input_keys
    if rows is not None:
        action.add_parent(_parent(rows))
    action.install()
    with pytest.raises(NodeException, match=message) if message else nullcontext():
        action.execute()
    popen.assert_not_called()
    assert action.get_buffer().size() == 0


@pytest.mark.parametrize("keyed_prompt", [False, True])
def test_multiline_stdin_and_utf8_output(action, popen, keyed_prompt):
    prompt = "Roses bloom.\n\n  Violets glow.\nGr\u00fc\u00dfe \U0001f339\n"
    action.instruction = "Keep every line break.\nPreserve indentation."
    if keyed_prompt:
        action.prompt, action.prompt_key = None, "task"
        action.add_parent(_parent([{"task": prompt}]))
    else:
        action.prompt = prompt
    # Echo stdin as bytes and emit UTF-8 diagnostics plus an invalid byte.
    popen.side_effect = lambda command, **options: REAL_POPEN(
        [sys.executable, "-c",
         "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read()); "
         "sys.stderr.buffer.write(bytes.fromhex('e29c9320ff'))"],
        **options,
    )
    action.install()
    action.execute()

    assert action.get_data()["stdout"] == [
        f"Instruction:\n{action.instruction}\n\nPrompt:\n{prompt}"
    ]
