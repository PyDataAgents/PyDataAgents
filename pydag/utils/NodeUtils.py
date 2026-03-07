from ..nodes.NodeException import NodeException


class NodeUtils:

    @staticmethod
    def validate_key_names(name: str, keys):
        """Validate the shared low-level contract for node key lists."""
        if not isinstance(keys, (list, tuple)):
            raise NodeException(f"{name} must be a list or tuple of unique non-empty strings")

        seen: set[str] = set()
        for key in keys:
            if not isinstance(key, str) or key.strip() == "":
                raise NodeException(f"{name} must contain only non-empty strings")
            normalized = key.strip()
            if normalized in seen:
                raise NodeException(f"{name} must contain unique entries")
            seen.add(normalized)
