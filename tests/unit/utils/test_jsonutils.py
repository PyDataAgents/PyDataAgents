import json

import pytest

from pydag.utils.JsonUtils import JsonUtils


def test_extract_fields_preserves_values_and_ignores_extra_fields():
    values = {"null": None, "bool": False, "int": 7, "float": 2.5, "text": "Grüße",
              "empty": [], "array": [1, None, {"a": True}], "object": {"nested": []}}
    payload = json.dumps({**values, "extra": "ignored"})
    result = JsonUtils.extract_fields(" \n" + payload + "\t", list(values))
    assert result == values
    for key, value in values.items():
        assert type(result[key]) is type(value)


@pytest.mark.parametrize("payload", ["", "not JSON", '{"a":}', 'prefix {"a": 1}',
                                    '{"a": 1} suffix', '{"a": 1}{"a": 2}',
                                    '```json\n{"a": 1}\n```', '{"a": NaN}',
                                    '{"a": Infinity}', '{"a": -Infinity}',
                                    '{"a": {"nested": NaN}}', None, {"a": 1}])
def test_extract_fields_rejects_invalid_json_as_value_error(payload):
    with pytest.raises(ValueError, match="valid JSON"):
        JsonUtils.extract_fields(payload, ["a"])


@pytest.mark.parametrize("payload", ['[]', '[{"a": 1}]', '"text"', "1", "true", "null"])
def test_extract_fields_requires_object(payload):
    with pytest.raises(ValueError, match="JSON object"):
        JsonUtils.extract_fields(payload, ["a"])


def test_extract_fields_reports_missing_field():
    with pytest.raises(ValueError, match="Missing required JSON field: path"):
        JsonUtils.extract_fields('{"file_name": "Invoice_2026.pdf"}', ["file_name", "path"])


def test_extract_fields_preserves_literal_names_and_selection_order():
    result = JsonUtils.extract_fields('{"first": 1, " second ": 2}', [" second ", "first"])
    assert list(result) == [" second ", "first"]
    assert result == {" second ": 2, "first": 1}


def test_extract_fields_allows_empty_generic_selection():
    assert JsonUtils.extract_fields('{"a": 1}', []) == {}


def test_existing_file_utilities_remain_compatible(tmp_path):
    path = tmp_path / "data.json"
    assert JsonUtils.read(path) is None
    assert JsonUtils.replace(path, "value", 2) is False
    JsonUtils.write(path, {"value": 1, "other": None})
    assert JsonUtils.read(path) == {"value": 1, "other": None}
    assert JsonUtils.replace(path, "value", [2, 3]) is True
    assert JsonUtils.read(path) == {"value": [2, 3], "other": None}
    assert JsonUtils.replace(path, "missing", 4) is False
