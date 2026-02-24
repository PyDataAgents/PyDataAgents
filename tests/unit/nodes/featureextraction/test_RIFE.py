import time
import matplotlib.pyplot as plt
from pydag.agents.AgentConfig import AgentConfig
from pydag.nodes.featureextraction.RIFEExtractor import RIFEExtractor
from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.SignalBuffer import SignalBuffer

# The tests mirror those in test_PSD but adapted for 256 RIFE features and key naming (-feature-rife-<i>)

def test_rife_sine_returns_256_zeros():
    # Single streaming sine signal; expect exactly 256 features when data available.
    signal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=signal, capacity=1000)
    sine_buff.install()
    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)

    rife = RIFEExtractor()
    rife.install()
    rife.add_parent(lba)

    for _ in range(10):
        time.sleep(0.5)
        rife.execute()
        data = rife.get_buffer().data(persistent=False)
        if data and len(data.values()) > 0:
            first_key = list(data.keys())[0]
            assert len(data[first_key]) == 256, f"Data length must be 256, but got: {len(data[first_key])}"
            for k, vec in data.items():
                assert all(x == 0 for x in vec), "All feature values must be zero for short input data"


def test_rife_short_input_zero_padding_behavior():
    # Single streaming sine signal; expect exactly 256 features when data available. Test what happens with short input data with length 10.
    signal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=signal, capacity=1000)
    sine_buff.install()
    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)

    rife = RIFEExtractor(sample_length=10)
    rife.install()
    rife.add_parent(lba)

    for _ in range(20):
        time.sleep(0.5)
        rife.execute()
        data = rife.get_buffer().data(persistent=False)
        if data and len(data.values()) > 0:
            first_key = list(data.keys())[0]
            assert len(data[first_key]) == 320, f"Data length must be 320, but got: {len(data[first_key])}"
            for k, vec in data.items():
                if k not in [AgentConfig.TIMESTAMPS, AgentConfig.INDEX]:
                    assert all(x == 0 for x in vec[-5:]), "The last 5 features are 0 because the method zero-pads to 320 if not enough valid intervals are found."
                else:
                    assert all(x != 0 for x in vec[-5:]), "Timestamps and indices should not be zero-padded."
                if k not in [AgentConfig.INDEX]:
                    assert all(x != 0 for x in vec[:50]), "The first 50 features must be != 0."


def test_rife_multiple_inference_samples_accumulate():
    # Single streaming sine signal; expect exactly 256 features when data available. Test what happens with short input data with length 10 and multiple inference samples.
    signal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=signal, capacity=1000)
    sine_buff.install()
    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)

    rife = RIFEExtractor(sample_length=100, min_inference_samples=5)
    rife.install()
    rife.add_parent(lba)

    for _ in range(20):
        time.sleep(0.5)
        rife.execute()
        data = rife.get_buffer().data(persistent=False)
        if data and len(data.values()) > 0:
            first_key = list(data.keys())[0]
            assert len(data[first_key]) == 320*5, f"Data length must be 320, but got: {len(data[first_key])}"
            assert len(list(data.keys())) == 2 + 2, "Expected exactly two feature vector keys" # +2 Because of timestamps and indices
            for k, vec in data.items():
                assert all(x != 0 for x in vec[:50]), "The first 50 features must be != 0."



def test_rife_cwru_dataset_changes_over_iterations():
    # CWRU dataset; ensure feature vectors differ across iterations when signal changes.
    dataset_buffer = DatasetBuffer("CWRU", sort_by_y=True)
    dataset_buffer.install()
    lba = LinkBufferAction()
    lba.set_buffer(dataset_buffer)

    rife = RIFEExtractor(sample_length=100, persistent=False)
    rife.install()
    rife.add_parent(lba)
    prev = None
    plt.ion()

    for _ in range(10):
        time.sleep(0.5)
        rife.execute()
        data = rife.get_buffer().data(persistent=False)
        if data and len(data.values()) > 0:
            first_key = list(data.keys())[0]
            if len(data[first_key]) == 320:
                plt.plot(list(data.values())[0], label=first_key)
                plt.pause(0.1)
                if prev is None:
                    prev = data[first_key]
                else:
                    assert prev != data[first_key], "Feature vector should change when underlying dataset sample changes"
                    prev = data[first_key]


def test_rife_cwru_multiple_inference_samples_length():
    # Multiple inference samples: accumulate 5*sample_length before inference if min_inference_samples=5.
    dataset_buffer = DatasetBuffer("CWRU", sort_by_y=True)
    dataset_buffer.install()
    lba = LinkBufferAction()
    lba.set_buffer(dataset_buffer)

    rife = RIFEExtractor(sample_length=100, min_inference_samples=5, persistent=False)
    rife.install()
    rife.add_parent(lba)

    for _ in range(10):
        time.sleep(0.5)
        rife.execute()
        data = rife.get_buffer().data(persistent=False)
        if data and len(data.values()) > 0:
            first_key = list(data.keys())[0]
            # Expect a single 320*5-length feature vector per inference run
            assert len(data[first_key]) in (0, 320*5), f"Data length must be 320*5 or 0, but got: {len(data[first_key])}"
