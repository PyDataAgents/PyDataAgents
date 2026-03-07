from dataclasses import dataclass, field
from typing import Dict, Tuple
import numpy as np
from scipy.stats import iqr

from ...agents.Agent import Agent
from ..LearningNode import LearningNode
from ...agents.AgentConfig import AgentConfig


@dataclass
class RIFEExtractor(LearningNode):
    """Random Interval Feature Extractor for time series data.

    Produces a 320 dimensional feature vector per input time series sample using
    sktime's RandomIntervalFeatureExtractor with:
        - n_intervals = 64
        - features = [np.median, np.std, iqr, np.min, np.max]
    yielding 64 * 5 = 320 features. Deterministic with random_state=42.

    Notes:
        - No learning required (pure feature extraction).
        - Accepts input dictionary with one or multiple keys; each key's value must
          be a 1D array-like time series. Generates a single feature vector per key.
        - Output keys follow the pattern: "<orig_key>-feature-rife-<i>" where i is the
          index (0..255) of the feature.
        - The extractor samples random start–end pairs. Depending on the sktime version, intervals that are invalid (e.g. zero or 1-length after an internal constraint) can get skipped. In such cases, the output feature vector is zero-padded to 320 length.
    """

    min_inference_samples: int = field(default=1, metadata={"description": "Number of samples to accumulate before inference."})
    # Override base class default: need at least MIN_SERIES_LENGTH points for meaningful random intervals
    sample_length: int = field(default=64, metadata={"description": "Length of each input time series sample; must be >= MIN_SERIES_LENGTH for meaningful features."})

    # Class-level minimal length constant
    MIN_SERIES_LENGTH: int = 64

    output_keys : list[str] = field(default_factory=list, metadata={"description": "optional explicit output keys; if empty, default naming is used"})

    def __post_init__(self):
        # Preconfigure preprocessing flags before parent init
        self.normalize = True  # z-score normalization
        self.nan_to_num = True  # sanitize NaN/Inf
        # Enforce minimal length
        if self.sample_length < self.MIN_SERIES_LENGTH:
            print(
                f"INFO: RIFEExtractor: sample_length={self.sample_length} is below the recommended minimum of {self.MIN_SERIES_LENGTH}. "
                f"Adjusting to {self.MIN_SERIES_LENGTH}."
            )
            self.sample_length = self.MIN_SERIES_LENGTH
        super().__post_init__()
        self.learning_required = False  # No learning step
        from sktime.transformations.panel.summarize import RandomIntervalFeatureExtractor

        self._ri_fe = RandomIntervalFeatureExtractor(
            n_intervals=64,
            features=[np.median, np.std, iqr, np.min, np.max],
            random_state=42,
        )

    def _on_install(self, agent: Agent = None):  # type: ignore[override]
        super()._on_install(agent)
        # Model attribute kept for symmetry with other extractors
        self._models = self._ri_fe

    # LearningNode abstract requirements
    def learn(self, data: dict, meta: dict | None = None) -> bool:  # noqa: D401
        return False  # never triggers further learning

    def _extract(self, series: np.ndarray) -> np.ndarray:
        """Run random interval feature extraction returning a 256-length vector (zero padded/truncated)."""
        # sktime expects shape (n_instances, n_variables, n_timepoints)
        panel3d = None
        if len(series.shape) == 2 and series.shape[0] == 1:
            series = series.flatten()
            panel3d = series.reshape(1, 1, -1)
        elif len(series.shape) == 2 and series.shape[0] > 1:
            panel3d = series.reshape(series.shape[0], 1, -1)
            
        if series.shape[-1] < self.MIN_SERIES_LENGTH:
            print(
                f"WARNING: RIFEExtractor: Input series length {series.shape[0]} < minimum {self.MIN_SERIES_LENGTH}; returning zeros."
            )
            z_size = 320 if len(series.shape) == 1 else series.shape[0] * 320
            return np.zeros(z_size, dtype=float)
        
        
        try:
            df = self._ri_fe.fit_transform(panel3d)
        except Exception:
            return np.zeros(320, dtype=float)
        values = df.to_numpy(dtype=float)
        if values.shape[-1] != 320:
            if values.shape[-1] > 320:
                values = values[..., :320]
            else:
                pad = np.zeros(320 - values.shape[-1], dtype=float)
                if values.shape[-1] < 300:
                    print(f"WARNING: RIFEExtractor: Extracted feature length {values.shape[-1]} < 300; Zero padding to 320.")
                pad_width = 320 - values.shape[-1]
                pad_shape = values.shape[:-1] + (pad_width,)
                pad = np.zeros(pad_shape, dtype=float)
                values = np.concatenate([values, pad], axis=-1)
        # Sanitize
        if not np.isfinite(values).all():
            values = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)
        return values.astype(float, copy=False)

    def infer(self, data: dict, meta: dict | None = None) -> Tuple[Dict, Dict]:  # noqa: D401
        forecast: Dict[str, list[float]] = {}
        for i, key in enumerate(data.keys()):
            series = np.asarray(data[key], dtype=np.float64)
            feats = self._extract(series).reshape(-1) # convert to numpy array and flatten - Stack all inference samples. It is similar to running n samples in sequence and adding them to the buffer.
            # Store as list under a single key (one list per original key)
            if len(data.keys()) == len(self.output_keys):
                forecast[self.output_keys[i]] = feats.tolist()
            else:
                forecast[self.__class__.__name__ + "-" + AgentConfig.FEATURE + "-" + f"{i}"] = feats.tolist()
        return forecast, None

__all__ = ["RIFEExtractor"]
