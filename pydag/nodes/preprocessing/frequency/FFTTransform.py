from dataclasses import dataclass, field
import math

import numpy as np

from pydag.agents.Agent import Agent
from pydag.nodes.Action import Action
from pydag.nodes.NodeException import NodeException
from pydag.utils.SignalUtils import SignalUtils

from ...BufferNode import BufferNode


@dataclass
class FFTTransform(BufferNode, Action):
    """ Transform input signals into one-sided frequency/amplitude spectra."""

    sample_rate: float = field(default=1.0, metadata={"description": "sample rate of the input signals in Hz"})

    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        if len(self.output_keys) > 0 and len(self.output_keys) != len(self.input_keys):
            raise NodeException(f"input_keys ({len(self.input_keys)}) and output_keys ({len(self.output_keys)}) must be the same length")
        if not math.isfinite(self.sample_rate) or self.sample_rate <= 0:
            raise NodeException("sample_rate must be a finite value greater than zero")
  
    def _on_execute(self):        
        data = self.get_parent_data()
        if not data:
            return

        if self.output_keys and len(self.output_keys) != len(data):
            raise NodeException(
                f"output_keys must contain one key for each input signal "
                f"({len(data)}), got {len(self.output_keys)}"
            )

        transformed = {}
        for index, (input_key, values) in enumerate(data.items()):
            try:
                signal = np.asarray(values, dtype=float)
            except (TypeError, ValueError) as exc:
                raise NodeException(
                    f"Input signal '{input_key}' must contain numeric samples"
                ) from exc

            if signal.ndim != 1 or signal.size == 0:
                raise NodeException(
                    f"Input signal '{input_key}' must be a non-empty one-dimensional sequence"
                )
            if not np.isfinite(signal).all():
                raise NodeException(
                    f"Input signal '{input_key}' must contain only finite samples"
                )

            frequencies, amplitudes = SignalUtils.fft(signal, self.sample_rate)
            output_key = (
                self.output_keys[index]
                if len(self.output_keys) > 0
                else f"{input_key}_fft"
            )
            output_key_freq = output_key + "_freq"
            transformed[output_key] = amplitudes.tolist()
            transformed[output_key_freq] = frequencies.tolist()

        self.add_data(transformed)
