"""AgentHarnessAction regressions; the live test requires an authenticated CLI."""
import json
from unittest.mock import MagicMock

import pytest

from pydag.agents.AgentElementException import AgentElementException
from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.NodeException import NodeException

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


class TestAgentHarnessActionJsonOutput:
    """Mocked JSON-output and text-compatibility regressions."""

    @pytest.fixture
    def configured_action(self, monkeypatch, tmp_path):
        """Mock the external boundary; no CLI or model calls."""
        monkeypatch.setattr('pydag.nodes.llm.AgentHarnessAction.shutil.which', lambda _: 'codex')
        process = MagicMock()
        process.__enter__.return_value = process
        process.communicate.return_value = ('{"value": "ok"}', 'diagnostics')
        process.returncode = 0
        launch = MagicMock(return_value=process)
        monkeypatch.setattr(AgentHarnessAction, '_execute_codex', launch)
        action = AgentHarnessAction(prompt='Find document', working_directory=str(tmp_path), output_mode='json', output_keys=['value'])
        boundary = process.communicate
        return action, boundary

    @staticmethod
    def _set_fields(action, keys):
        action.output_keys = list(keys)

    @staticmethod
    def _set_answers(action, boundary, answers):
        boundary.side_effect = [(answer, 'diagnostics') for answer in answers]

    @staticmethod
    def _parent(rows):
        parent = LinkBufferAction()
        parent.install()
        parent.add_data(rows)
        return parent

    @staticmethod
    def _user_data(action):
        data = action.get_data()
        buffer = action.get_buffer()
        data.pop(buffer.timestamps_key, None)
        data.pop(buffer.index_key, None)
        return data

    def test_extracts_fields_and_ignores_extra_fields(self, configured_action):
        action, boundary = configured_action
        self._set_fields(action, ['file_name', 'path'])
        payload = {'file_name': 'Invoice_2026.pdf', 'path': 'C:\\Documents\\Finance', 'original_question': 'model must not overwrite input', 'extra': 42}
        self._set_answers(action, boundary, [' \n' + json.dumps(payload) + '\t '])
        action.install()
        action.execute()
        expected = {'file_name': [payload['file_name']], 'path': [payload['path']]}
        assert self._user_data(action) == expected
        assert action.get_buffer().size() == 1
        boundary.assert_called_once()

    @pytest.mark.parametrize(
        'value',
        [
            None,
            True,
            False,
            0,
            3.25,
            '',
            'Grüße',
            [],
            [1, None, {'a': False}],
            {'nested': []},
        ],
    )
    def test_preserves_values_in_one_row(self, configured_action, value):
        action, boundary = configured_action
        self._set_answers(action, boundary, [json.dumps({'value': value})])
        action.install()
        action.execute()
        result = action.get_data()['value']
        assert result == [value]
        assert type(result[0]) is type(value)
        assert action.get_buffer().size() == 1

    def test_mixed_arrays_and_scalars_are_one_row(self, configured_action):
        action, boundary = configured_action
        payload = {'empty': [], 'items': [1, 2, 3], 'scalar': None, 'object': {'nested': [1]}}
        self._set_fields(action, list(payload))
        self._set_answers(action, boundary, [json.dumps(payload)])
        action.install()
        action.execute()
        for key, value in payload.items():
            assert action.get_data()[key] == [value]
        assert action.get_buffer().size() == 1

    @pytest.mark.parametrize(
        'answer, message',
        [
            ('not JSON', 'valid JSON'),
            ('{"value":}', 'valid JSON'),
            ('{"value": 1} trailing text', 'valid JSON'),
            ('prefix {"value": 1}', 'valid JSON'),
            ('```json\n{"value": 1}\n```', 'valid JSON'),
            ('{"value": 1} {"value": 2}', 'valid JSON'),
            ('{"value": NaN}', 'valid JSON'),
            ('{"value": Infinity}', 'valid JSON'),
            ('{"value": -Infinity}', 'valid JSON'),
            ('{"value": {"nested": NaN}}', 'valid JSON'),
            ('[{"value": 1}]', 'JSON object'),
            ('"value"', 'JSON object'),
            ('null', 'JSON object'),
            ('true', 'JSON object'),
            ('12', 'JSON object'),
            ('{}', 'Missing required JSON field.*value'),
            (None, 'valid JSON'),
            ({'value': 1}, 'valid JSON'),
        ],
    )
    def test_invalid_answer_never_publishes_partial_row(self, configured_action, answer, message):
        action, boundary = configured_action
        self._set_answers(action, boundary, [answer])
        action.install()
        with pytest.raises(NodeException, match=message) as error:
            action.execute()
        assert isinstance(error.value.__cause__, ValueError)
        assert action.get_buffer().size() == 0

    @pytest.mark.parametrize(
        'keys',
        [
            None,
            'value',
            [],
            [''],
            [' '],
            [42],
            ['value', 42],
            ['value', 'value'],
            ['value', ' value '],
        ],
    )
    def test_invalid_output_keys_fail_before_invocation(self, configured_action, keys):
        action, boundary = configured_action
        action.output_keys = keys
        with pytest.raises(AgentElementException):
            action.install()
        boundary.assert_not_called()

    @pytest.mark.parametrize('mode', ['JSON', '', None, 42, []])
    def test_invalid_mode_fails_before_invocation(self, configured_action, mode):
        action, boundary = configured_action
        action.output_mode = mode
        with pytest.raises(AgentElementException, match='output_mode'):
            action.install()
        boundary.assert_not_called()

    @pytest.mark.parametrize('key', ['stderr', 'exit_code', 'timestamps', 'index'])
    def test_reserved_output_keys_fail_before_invocation(self, configured_action, key):
        action, boundary = configured_action
        self._set_fields(action, [key])
        with pytest.raises(AgentElementException, match='reserved'):
            action.install()
        boundary.assert_not_called()

    @pytest.mark.parametrize('key', ['record_id', 'record_time'])
    def test_custom_buffer_metadata_is_reserved(self, configured_action, key):
        action, boundary = configured_action
        action.set_buffer(DictBuffer(index_key='record_id', timestamps_key='record_time'))
        self._set_fields(action, [key])
        with pytest.raises(AgentElementException, match='reserved'):
            action.install()
        boundary.assert_not_called()

    def test_literal_field_names_are_not_trimmed(self, configured_action):
        action, boundary = configured_action
        self._set_fields(action, [' value '])
        self._set_answers(action, boundary, ['{" value ": 3}'])
        action.install()
        action.execute()
        assert action.get_data()[' value '] == [3]

    @pytest.mark.parametrize('persistent', [False, True])
    @pytest.mark.parametrize('n', [0, 2])
    def test_multiple_inputs_preserve_association(self, configured_action, persistent, n):
        action, boundary = configured_action
        parent = self._parent([{'task': 'first'}, {'task': 'second'}, {'task': 'third'}])
        action.add_parent(parent)
        action.input_keys = ['task']
        action.n, action.persistent = (n, persistent)
        action.prompt, action.prompt_key = (None, 'task')
        selected = ['first', 'second', 'third'][:n or None]
        self._set_answers(action, boundary, [json.dumps({'value': task}) for task in selected])
        action.install()
        action.execute()
        assert action.get_data()['value'] == selected
        actual_inputs = [call.kwargs['input'] for call in boundary.call_args_list]
        assert actual_inputs == selected
        assert parent.get_buffer().size() == (3 if persistent else 3 - len(selected))

    def test_later_invalid_response_keeps_only_prior_success(self, configured_action):
        action, boundary = configured_action
        action.add_parent(self._parent([{'task': 'first'}, {'task': 'second'}, {'task': 'third'}]))
        action.prompt, action.prompt_key = (None, 'task')
        self._set_fields(action, ['value', 'required'])
        self._set_answers(action, boundary, ['{"value": 1, "required": null}', '{"value": 2}', '{"value": 3, "required": 3}'])
        action.install()
        with pytest.raises(NodeException, match='required'):
            action.execute()
        assert action.get_data()['value'] == [1]
        assert action.get_data()['required'] == [None]
        assert action.get_buffer().size() == 1
        assert boundary.call_count == 2

    def test_text_mode_compatibility(self, configured_action):
        action, boundary = configured_action
        action.output_mode = 'text'
        action.output_keys = ['response']
        self._set_answers(action, boundary, ['unstructured answer\n'])
        action.install()
        action.execute()
        expected = {'response': ['unstructured answer\n']}
        assert self._user_data(action) == expected

    def test_child_receives_json_arrays_without_row_expansion(self, configured_action):
        action, boundary = configured_action
        self._set_answers(action, boundary, ['{"value": [1, null, 3]}'])
        action.install()
        action.execute()
        child = LinkBufferAction(input_keys=['value'])
        child.add_parent(action)
        child.install()
        assert child.get_parent_data(by_rows=True) == [{'value': [1, None, 3]}]

    def test_harness_defaults_and_text_exit_code_compatibility(self, monkeypatch, tmp_path):
        monkeypatch.setattr('pydag.nodes.llm.AgentHarnessAction.shutil.which', lambda _: 'codex')
        process = MagicMock()
        process.__enter__.return_value = process
        process.communicate.return_value = ('raw response', 'error')
        process.returncode = 1
        monkeypatch.setattr(AgentHarnessAction, '_execute_codex', MagicMock(return_value=process))
        action = AgentHarnessAction(prompt='task', working_directory=str(tmp_path))
        action.install()
        action.execute()
        assert self._user_data(action) == {'stdout': ['raw response']}

    def test_harness_json_rejects_failed_process(self, configured_action):
        action, boundary = configured_action
        action._execute_codex.return_value.returncode = 7
        action.install()
        with pytest.raises(NodeException, match='exit code 7'):
            action.execute()
        assert action.get_buffer().size() == 0
