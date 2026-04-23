import re

from pydag.nodes.NodeException import NodeException


class NodeUtils:

    TYPE_STRING = "type:string"
    TYPE_NUMBER = "type:number"
    _SLICE_PATTERN = re.compile(r"^\s*(-?\d*)\s*:\s*(-?\d*)\s*(?::\s*(-?\d*)\s*)?$")

    @staticmethod
    def validate_key_names(name: str, keys, allow_special: bool = False):
        if not isinstance(keys, (list, tuple)):
            raise NodeException(f"{name} must be a list or tuple")

        seen = set()
        for key in keys:
            if not isinstance(key, str) or key.strip() == "":
                raise NodeException(f"{name} must contain only non-empty strings")
            normalized = key.strip()
            if normalized in seen:
                raise NodeException(f"{name} must contain unique entries")
            seen.add(normalized)
            if allow_special:
                NodeUtils._validate_special_selector(name, normalized)

    @staticmethod
    def filter_data_by_selectors(data: dict, selectors: list[str]) -> dict:
        if not data or len(selectors) == 0:
            return data if data is not None else {}

        keys = list(data.keys())
        selected = []
        seen = set()
        for selector in selectors:
            matching = NodeUtils._select_keys(keys, data, selector.strip())
            for key in matching:
                if key not in seen:
                    selected.append(key)
                    seen.add(key)
        return {key: data[key] for key in selected}

    @staticmethod
    def _validate_special_selector(name: str, selector: str):
        if selector.lower() in {NodeUtils.TYPE_STRING, NodeUtils.TYPE_NUMBER}:
            return
        if selector.lower().startswith("type:"):
            raise NodeException(f"{name} supports only type:string and type:number")

    @staticmethod
    def _select_keys(keys: list[str], data: dict, selector: str) -> list[str]:
        selector_lower = selector.lower()
        if selector_lower == NodeUtils.TYPE_STRING:
            return [key for key in keys if isinstance(NodeUtils._sample_value(data[key]), str)]
        if selector_lower == NodeUtils.TYPE_NUMBER:
            return [ key for key in keys if isinstance(NodeUtils._sample_value(data[key]), (int, float, bool))]

        match = NodeUtils._SLICE_PATTERN.match(selector)
        if match:
            return keys[slice(*(NodeUtils._to_int(value) for value in match.groups()))]

        return [selector] if selector in keys else []

    @staticmethod
    def _sample_value(value):
        if isinstance(value, list):
            for item in value:
                if item is not None:
                    return item
            return None
        return value

    @staticmethod
    def _to_int(value: str):
        return None if value is None or value == "" else int(value)
