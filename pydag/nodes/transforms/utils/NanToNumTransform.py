from dataclasses import dataclass, field
from typing import Dict, Any
from ...transforms.Transform import Transform
import numpy as np

@dataclass
class NanToNumTransform(Transform):
    """Transform that replaces NaN and +/-Inf values in each entry with finite numbers (default 0.0).

    Parameters
    ----------
    nan_value : float
        Value to substitute for NaN.
    posinf_value : float
        Value to substitute for +Inf.
    neginf_value : float
        Value to substitute for -Inf.
    as_list : bool
        If True, output is converted back to list when original value was list-like.
    """
    nan_value: float = field(default=0.0, metadata={"description": "Replacement for NaN."})
    posinf_value: float = field(default=0.0, metadata={"description": "Replacement for +Inf."})
    neginf_value: float = field(default=0.0, metadata={"description": "Replacement for -Inf."})

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:  # noqa: D401
        cleaned: Dict[str, Any] = {}
        for k, v in data.items():
            arr = np.asarray(v)
            if not np.isfinite(arr).all():
                arr = np.nan_to_num(arr, nan=self.nan_value, posinf=self.posinf_value, neginf=self.neginf_value)
            cleaned[k] = arr.tolist() if not np.isscalar(arr) else list(arr)
        return cleaned

__all__ = ["NanToNumTransform"]
