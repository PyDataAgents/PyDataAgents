import time
import matplotlib.pyplot as plt
import numpy as np
from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.nodes.featureextraction.PSDExtractor import PSDExtractor
from pydag.agents.AgentKeywords import AgentKeywords


# Test one inference sample as well as multiple inference samples on different datasets.

def test_psd_streaming_sine_returns_257():
    # Test if always 257 values are returned
    signal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=signal, capacity=1000)
    sine_buff.install()
    lba = LinkBufferAction()
    lba._buffer = sine_buff

    PSD = PSDExtractor()
    PSD.install()
    PSD.add_parent(lba)

    for i in range(10):
        print(i)
        time.sleep(0.5)
        PSD.execute()
        data = PSD._buffer.data(persistent=False)
        if len(data.values()) > 0:
            assert len(data[list(data.keys())[0]]) == 257, f"Data length must be 257, but got: {len(data[list(data.keys())[0]])}"


def test_psd_welch_keys_and_length_persistent():
    # Test if always 257 values are returned with a samople length of 100 and the signal is not changing
    signal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=signal, capacity=10**12)
    sine_buff.install()
    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)
    signal = None

    PSD = PSDExtractor(sample_length=100, persistent=True)
    PSD.install()
    PSD.add_parent(lba)
    #plt.ion()
    for i in range(10):
        print(i)
        time.sleep(0.5)
        PSD.execute()
        data = PSD.get_buffer().data(persistent=False)
        if data: 
            assert any([len(data[list(data.keys())[0]]) == 257, len(data[list(data.keys())[0]]) == 0]), f"Data length must be 257 or 0, but got: {len(data[list(data.keys())[0]])}"
            assert len(list(data.keys())) == 2
            assert all([key in data.keys() for key in ["timestamps-feature-welch-0","values-feature-welch-1"]]), f"Keys must be ['timestamps-feature-welch-0','values-feature-welch-1'], but got: {list(data.keys())}"
            if len(data[list(data.keys())[0]]) == 257:
                if signal is None:
                    signal = data[list(data.keys())[1]]
                else:
                    assert signal == data[list(data.keys())[1]], "Signal must be the same in each iteration, since the sine is not changing"
                    signal = data[list(data.keys())[1]]
            #plt.plot(data[list(data.keys())[0]])
            #plt.pause(0.1)


def test_psd_feature_key_naming_pattern():
    """Ensure PSDExtractor returns keys `ClassName-<FEATURE>-<i>` using cname()."""
    psd = PSDExtractor(min_inference_samples=1, persistent=False)
    psd.install()

    n = 512
    data = {
        "dim0": np.zeros(n).tolist(),
        "dim1": np.ones(n).tolist(),
    }

    # Retry until data exists
    attempts = 0
    forecast = {}
    while attempts < 5 and (not isinstance(forecast, dict) or len(forecast) == 0):
        forecast, _ = psd.infer(data, meta=None)
        attempts += 1
        time.sleep(0.1)
    assert isinstance(forecast, dict) and len(forecast) > 0
    for idx, k in enumerate(forecast.keys()):
        expected_key = PSDExtractor.cname() + "-" + AgentKeywords.FEATURE + "-" + f"{idx}"
        assert k == expected_key


def test_psd_output_keys_match_length():
    """When output_keys length matches number of inputs, use provided keys."""
    custom_keys = ["k0", "k1"]
    psd = PSDExtractor(min_inference_samples=1, persistent=False, output_keys=custom_keys)
    psd.install()

    n = 512
    data = {
        "dim0": np.zeros(n).tolist(),
        "dim1": np.ones(n).tolist(),
    }

    attempts = 0
    forecast = {}
    while attempts < 5 and (not isinstance(forecast, dict) or len(forecast) == 0):
        forecast, _ = psd.infer(data, meta=None)
        attempts += 1
        time.sleep(0.1)
    assert set(forecast.keys()) == set(custom_keys)


def test_psd_output_keys_mismatch_uses_default():
    """When output_keys length mismatches, fall back to default naming."""
    custom_keys = ["only-one-key"]
    psd = PSDExtractor(min_inference_samples=1, persistent=False, output_keys=custom_keys)
    psd.install()

    n = 512
    data = {
        "dim0": np.zeros(n).tolist(),
        "dim1": np.ones(n).tolist(),
    }

    attempts = 0
    forecast = {}
    while attempts < 5 and (not isinstance(forecast, dict) or len(forecast) == 0):
        forecast, _ = psd.infer(data, meta=None)
        attempts += 1
        time.sleep(0.1)
    # Two inputs -> expect default naming for both
    expected = {
        PSDExtractor.__name__ + "-" + AgentKeywords.FEATURE + "-" + "0",
        PSDExtractor.__name__ + "-" + AgentKeywords.FEATURE + "-" + "1",
    }
    assert set(forecast.keys()) == expected


def test_psd_ucr_dataset_keys_and_length():
    # Test if always 257 values are returned for UCR Dataset
    dataset_buffer = DatasetBuffer("Wine", sort_by_y=True)
    dataset_buffer.install()
    lba = LinkBufferAction()
    lba.set_buffer(dataset_buffer)

    PSD = PSDExtractor(sample_length=100, persistent=False, ignore_keys=["index", "timestamps"])
    PSD.install()
    PSD.add_parent(lba)
    #plt.ion()
    for i in range(10):
        print(i)
        time.sleep(0.5)
        PSD.execute()
        data = PSD.get_buffer().data(persistent=False)
        if data and len(data.values()) > 0:
            assert any([len(data[list(data.keys())[0]]) == 257, len(data[list(data.keys())[0]]) == 0]), f"Data length must be 257 or 0, but got: {len(data[list(data.keys())[0]])}"
            assert len(list(data.keys())) == 2 + 2 # Because of timestamps and indices
            assert all([key in data.keys() for key in [PSDExtractor.__name__ + "-" + AgentKeywords.FEATURE + "-" + "0", PSDExtractor.__name__ + "-" + AgentKeywords.FEATURE + "-" + "1",]]), f"Keys must be {PSDExtractor.__name__ + '-' + AgentKeywords.FEATURE + '-0', PSDExtractor.__name__ + '-' + AgentKeywords.FEATURE + '-1'}, but got: {list(data.keys())}"
            #plt.plot(data[list(data.keys())[0]])
            #plt.pause(0.1)

def test_psd_cwru_dataset_changes_and_default_keys():
    # Test if always 257 values are returned for CWRU data and signal is changing
    dataset_buffer = DatasetBuffer("CWRU", sort_by_y=True)
    dataset_buffer.install()
    lba = LinkBufferAction()
    lba.set_buffer(dataset_buffer)
    signal = None
    PSD = PSDExtractor(sample_length=100, persistent=False)
    PSD.install()
    PSD.add_parent(lba)
    #plt.ion()
    for i in range(10):
        print(i)
        time.sleep(0.5)
        PSD.execute()
        data = PSD.get_buffer().data(persistent=False)
        if data and len(data.values()) > 0:
            assert any([len(data[list(data.keys())[0]]) == 257, len(data[list(data.keys())[0]]) == 0]), f"Data length must be 257 or 0, but got: {len(data[list(data.keys())[0]])}"
            assert len(list(data.keys())) == 2 + 2 # Because of timestamps and indices
            assert all([key in data.keys() for key in [PSDExtractor.__name__ + "-" + AgentKeywords.FEATURE + "-" + "0", PSDExtractor.__name__ + "-" + AgentKeywords.FEATURE + "-" + "1",]]), f"Keys must be {PSDExtractor.__name__ + '-' + AgentKeywords.FEATURE + '-0', PSDExtractor.__name__ + '-' + AgentKeywords.FEATURE + '-1'}, but got: {list(data.keys())}"
            assert all([key in data.keys() for key in [AgentKeywords.INDEX, AgentKeywords.TIMESTAMPS]]), f"Keys must contain {AgentKeywords.INDEX, AgentKeywords.TIMESTAMPS}, but got: {list(data.keys())}" 
            if len(data[list(data.keys())[0]]) == 257:
                if signal is None:
                    signal = data[list(data.keys())[0]]
                else:
                    assert signal != data[list(data.keys())[0]], "Signal must be different in each iteration, since the data is changing"
                    signal = data[list(data.keys())[0]]
            #plt.plot(data[list(data.keys())[0]])
            #plt.pause(0.1)


def test_psd_cwru_multiple_inference_samples():
    # Test if always 257*5 values are returned for CWRU data and signal is changing when 5 inference samples are used
    dataset_buffer = DatasetBuffer("CWRU", sort_by_y=True)
    dataset_buffer.install()
    lba = LinkBufferAction()
    lba.set_buffer(dataset_buffer)
    signal = None
    PSD = PSDExtractor(sample_length=100, min_inference_samples=5, persistent=False)
    PSD.install()
    PSD.add_parent(lba)
    #plt.ion()
    for i in range(10):
        print(i)
        time.sleep(0.5)
        PSD.execute()
        data = PSD.get_buffer().data(persistent=False)
        if data and len(data.values()) > 0:
            assert any([len(data[list(data.keys())[0]]) == 257*5, len(data[list(data.keys())[0]]) == 0]), f"Data length must be 257 or 0, but got: {len(data[list(data.keys())[0]])}"
            assert len(list(data.keys())) == 2 + 2 # Because of timestamps and indices
            assert all([key in data.keys() for key in [PSDExtractor.__name__ + "-" + AgentKeywords.FEATURE + "-" + "0", PSDExtractor.__name__ + "-" + AgentKeywords.FEATURE + "-" + "1",]]), f"Keys must be {PSDExtractor.__name__ + '-' + AgentKeywords.FEATURE + '-0', PSDExtractor.__name__ + '-' + AgentKeywords.FEATURE + '-1'}, but got: {list(data.keys())}"
            if len(data[list(data.keys())[0]]) == 257*5:
                if signal is None:
                    signal = data[list(data.keys())[0]]
                else:
                    assert signal != data[list(data.keys())[0]], "Signal must be different in each iteration, since the data is changing"
                    signal = data[list(data.keys())[0]]
            #plt.plot(data[list(data.keys())[0]])
            #plt.pause(0.1)
