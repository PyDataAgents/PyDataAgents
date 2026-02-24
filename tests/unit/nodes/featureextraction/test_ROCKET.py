import time
import numpy as np
from pydag.buffers.DatasetBuffer import DatasetBuffer, DatasetNames
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.featureextraction.ROCKETExtractor import ROCKETExtractor
from pydag.agents.AgentConfig import AgentConfig


def test_rocket_exec_produces_n_length():
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    lba = LinkBufferAction()
    lba.set_buffer(sds)
    lba.install()

    rocket = ROCKETExtractor(min_learning_samples=10, min_inference_samples=10, input_keys=["values"], persistent=False)
    rocket.install()
    rocket.add_parent(lba)

    n = 10

    for i in range(10):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        rocket.execute()
        data = rocket.get_buffer().data(n=10, persistent=False)
        if data is not None:
            assert type(data) == dict
            for key in data.keys():
                assert type(data[key]) == list
                if len(data[key]) > 0:
                    assert len(data[key]) == n


def test_rocket_feature_key_naming_pattern():
    """Ensure ROCKETExtractor returns keys `ClassName-<FEATURE>-<i>` when
    number of input keys differs from `output_keys` length.
    """
    rocket = ROCKETExtractor(num_of_kernels=5, min_learning_samples=1, min_inference_samples=1, persistent=False)
    rocket.install()

    n = 64
    learn_signal = np.linspace(0, 1, n).tolist()
    learn_data = {"train": learn_signal}
    rocket.learn(learn_data, meta=None)

    sig0 = np.sin(np.linspace(0, 2*np.pi, n)).tolist()
    sig1 = np.cos(np.linspace(0, 2*np.pi, n)).tolist()
    infer_data = {
        "dim0": [sig0],
        "dim1": [sig1],
    }

    attempts = 0
    forecast = {}
    while attempts < 5 and (not isinstance(forecast, dict) or len(forecast) == 0):
        forecast, _ = rocket.infer(infer_data, meta=None)
        attempts += 1
        time.sleep(0.1)
    assert isinstance(forecast, dict) and len(forecast) > 0
    for idx, k in enumerate(forecast.keys()):
        expected_key = ROCKETExtractor.__name__ + "-" + AgentConfig.FEATURE + "-" + f"{idx}"
        assert k == expected_key


def test_rocket_output_keys_match_length():
    """When output_keys length matches number of inputs, use provided keys."""
    rocket = ROCKETExtractor(num_of_kernels=5, min_learning_samples=1, min_inference_samples=1, persistent=False,
                             output_keys=["r0", "r1"])
    rocket.install()

    n = 64
    learn_signal = np.linspace(0, 1, n).tolist()
    rocket.learn({"train": learn_signal}, meta=None)

    sig0 = np.sin(np.linspace(0, 2*np.pi, n)).tolist()
    sig1 = np.cos(np.linspace(0, 2*np.pi, n)).tolist()
    infer_data = {
        "dim0": [sig0],
        "dim1": [sig1],
    }
    attempts = 0
    forecast = {}
    while attempts < 5 and (not isinstance(forecast, dict) or len(forecast) == 0):
        forecast, _ = rocket.infer(infer_data, meta=None)
        attempts += 1
        time.sleep(0.1)
    assert set(forecast.keys()) == {"r0", "r1"}


def test_rocket_output_keys_mismatch_uses_default():
    """When output_keys length mismatches, fall back to default naming."""
    rocket = ROCKETExtractor(num_of_kernels=5, min_learning_samples=1, min_inference_samples=1, persistent=False,
                             output_keys=["only-one-key"])
    rocket.install()

    n = 64
    learn_signal = np.linspace(0, 1, n).tolist()
    rocket.learn({"train": learn_signal}, meta=None)

    sig0 = np.sin(np.linspace(0, 2*np.pi, n)).tolist()
    sig1 = np.cos(np.linspace(0, 2*np.pi, n)).tolist()
    infer_data = {
        "dim0": [sig0],
        "dim1": [sig1],
    }
    attempts = 0
    forecast = {}
    while attempts < 5 and (not isinstance(forecast, dict) or len(forecast) == 0):
        forecast, _ = rocket.infer(infer_data, meta=None)
        attempts += 1
        time.sleep(0.1)
    expected = {
        ROCKETExtractor.__name__ + "-" + AgentConfig.FEATURE + "-" + "0",
        ROCKETExtractor.__name__ + "-" + AgentConfig.FEATURE + "-" + "1",
    }
    assert set(forecast.keys()) == expected
