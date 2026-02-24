import time
from pydag.nodes.featureextraction.ChronosExtractor import ChronosExtractor
from pydag.agents.AgentConfig import AgentConfig
from pydag.buffers.DatasetBuffer import DatasetBuffer, DatasetNames
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.SignalBuffer import SignalBuffer


def test_chronos_streaming_sine_outputs_bounds():

    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)

    
    chronos = ChronosExtractor()
    chronos.install()

    chronos.add_parent(lba)

    for i in range(10):
        time.sleep(0.5)
        chronos.execute()
        data = chronos.get_buffer().data(n=10)
        if len(data.values()) > 0:
            assert len(data[list(data.keys())[0]]) > 0 and len(data[list(data.keys())[0]]) <= 10, f"Data length out of bounds: {len(data[list(data.keys())[0]])}"



def test_chronos_exec_produces_n_length():
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.set_buffer(sds)
    lba.install()

    chronos = ChronosExtractor(sample_length=10, persistent=False, input_keys=["values"])
    chronos.install()

    chronos.add_parent(lba)
    
    n = 10

    for i in range(10):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        chronos.execute()
        data = chronos.get_buffer().data(n=10, persistent=False)
        if data is not None:
            assert type(data) == dict
            for key in data.keys():
                assert type(data[key]) == list
                if len(data[key]) > 0:
                    assert len(data[key]) == n


def test_chronos_normalize_exec_produces_n_length():

    # With data normalization
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.set_buffer(sds)
    lba.install()

    chronos = ChronosExtractor(sample_length=10, min_inference_samples=10, persistent=False, normalize=True, input_keys=["values"])
    chronos.install()

    chronos.add_parent(lba)
    
    n = 10

    for i in range(10):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        chronos.execute()
        data = chronos.get_buffer().data(n=10, persistent=False)
        if data is not None:
            assert type(data) == dict
            for key in data.keys():
                assert type(data[key]) == list
                if len(data[key]) > 0:
                    assert len(data[key]) == n


def test_chronos_feature_key_naming_pattern():
    """Ensure ChronosExtractor returns keys `ClassName-<FEATURE>-<i>` when
    output_keys length does not match number of input keys.
    """
    CE = ChronosExtractor(min_inference_samples=1, persistent=False)
    CE.install()

    data = {
        "dim0": [1.0, 2.0, 3.0],
        "dim1": [4.0, 5.0, 6.0],
    }

    # Retry until data exists
    attempts = 0
    forecast = {}
    while attempts < 5 and (not isinstance(forecast, dict) or len(forecast) == 0):
        forecast, _ = CE.infer(data, meta=None)
        attempts += 1
        time.sleep(0.1)
    assert isinstance(forecast, dict) and len(forecast) > 0
    for idx, k in enumerate(forecast.keys()):
        expected_key = ChronosExtractor.__name__ + "-" + AgentConfig.FEATURE + "-" + f"{idx}"
        assert k == expected_key


def test_chronos_output_keys_match_length():
    """When output_keys length matches number of inputs, use provided keys."""
    custom_keys = ["c0", "c1"]
    CE = ChronosExtractor(min_inference_samples=1, persistent=False, output_keys=custom_keys)
    CE.install()

    data = {
        "dim0": [1.0, 2.0, 3.0],
        "dim1": [4.0, 5.0, 6.0],
    }

    attempts = 0
    forecast = {}
    while attempts < 5 and (not isinstance(forecast, dict) or len(forecast) == 0):
        forecast, _ = CE.infer(data, meta=None)
        attempts += 1
        time.sleep(0.1)
    assert set(forecast.keys()) == set(custom_keys)


def test_chronos_output_keys_mismatch_uses_default():
    """When output_keys length mismatches, fall back to default naming."""
    custom_keys = ["only-one-key"]
    CE = ChronosExtractor(min_inference_samples=1, persistent=False, output_keys=custom_keys)
    CE.install()

    data = {
        "dim0": [1.0, 2.0, 3.0],
        "dim1": [4.0, 5.0, 6.0],
    }

    attempts = 0
    forecast = {}
    while attempts < 5 and (not isinstance(forecast, dict) or len(forecast) == 0):
        forecast, _ = CE.infer(data, meta=None)
        attempts += 1
        time.sleep(0.1)
    expected = {
        ChronosExtractor.__name__ + "-" + AgentConfig.FEATURE + "-" + "0",
        ChronosExtractor.__name__ + "-" + AgentConfig.FEATURE + "-" + "1",
    }
    assert set(forecast.keys()) == expected

