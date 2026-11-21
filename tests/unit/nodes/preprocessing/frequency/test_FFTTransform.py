import numpy as np
import pytest

from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.NodeException import NodeException
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.preprocessing.frequency.FFTTransform import FFTTransform


def _create_transform(input_data, **kwargs):
    source_buffer = DictBuffer(index_enabled=False, timestamps_enabled=False)
    source_buffer.install()
    source_buffer.push(input_data)

    source = LinkBufferAction()
    source.set_buffer(source_buffer)
    source.install()

    output_buffer = DictBuffer(index_enabled=False, timestamps_enabled=False)
    output_buffer.install()
    transform = FFTTransform(**kwargs)
    transform.set_buffer(output_buffer)
    transform.add_parent(source)
    transform.install()
    return transform


def test_fft_transform_uses_input_keys_with_fft_suffix_and_sample_rate():
    sample_rate = 8.0
    samples = np.sin(2 * np.pi * np.arange(8) / 8).tolist()
    transform = _create_transform(
        {"vibration": samples},
        input_keys=["vibration"],
        sample_rate=sample_rate,
    )

    transform.execute()

    spectrum = transform.get_buffer().data()["vibration_fft"]
    assert len(spectrum) == 5
    assert spectrum[1] == pytest.approx([1.0, 1.0])


def test_fft_transform_uses_explicit_output_keys():
    transform = _create_transform(
        {"vibration": [1.0, 0.0, -1.0, 0.0]},
        input_keys=["vibration"],
        output_keys=["spectrum"],
        sample_rate=4.0,
    )

    transform.execute()

    assert "spectrum" in transform.get_buffer().data()


@pytest.mark.parametrize("sample_rate", [0.0, -1.0, float("inf"), None])
def test_fft_transform_rejects_invalid_sample_rate(sample_rate):
    transform = _create_transform(
        {"vibration": [1.0, 0.0]},
        input_keys=["vibration"],
        sample_rate=sample_rate,
    )

    with pytest.raises(NodeException, match="sample_rate"):
        transform.execute()


def test_fft_transform_rejects_output_key_count_mismatch():
    transform = _create_transform(
        {"first": [1.0, 0.0], "second": [0.0, 1.0]},
        input_keys=["first", "second"],
        output_keys=["only_one"],
        sample_rate=2.0,
    )

    with pytest.raises(NodeException, match="output_keys"):
        transform.execute()
