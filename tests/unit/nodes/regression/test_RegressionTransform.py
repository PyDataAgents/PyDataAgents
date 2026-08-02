import matplotlib.pyplot as plt
import time


from pydag.nodes.regression.RegressionTransform import RegressionTransform
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction


def test_basic_tirex_prediction_length():
    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)

    prediction_length = 10

    cd = RegressionTransform(n=10, learning_required=False, min_inference_samples=20, persistent=False, prediction_length=prediction_length)
    cd.install()
    cd.add_parent(lba)

    for i in range(10):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        cd.execute()
        data = cd.get_buffer().data(n=prediction_length)
        print(data)
        if data is not None:
            assert type(data) == dict
            for key in data.keys():
                assert type(data[key]) == list
                if len(data[key]) > 0:
                    assert len(data[key]) == prediction_length

def test_signal_buffer_data_length_cap():
    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()

    for i in range(10):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        data = sine_buff.data(n=100)
        print(data)
        if len(list(data.values())[0]) > 0:
            assert len(list(data.values())[0]) <= 100, f"Data length exceeded: {len(list(data.values())[0])}"



def test_models_chronos_and_tirex_prediction_length():
    for name in ["CHRONOS", "Tirex"]:
        singal = Sine(f=1, a=1, p=0, n=0.1)
        sine_buff = SignalBuffer(signal=singal, capacity=1000)
        sine_buff_2 = SignalBuffer(signal=singal, capacity=1000)
        sine_buff.install()
        sine_buff_2.install()

        lba = LinkBufferAction()
        lba.set_buffer(sine_buff) 

        lba_2 = LinkBufferAction()
        lba_2.set_buffer(sine_buff_2)

        prediction_length = 30
        n= 100

        cd = RegressionTransform(model_name= name, n=n, learning_required=False, min_inference_samples=n, persistent=False, prediction_length=prediction_length)
        cd.install()
        cd.add_parent(lba)
        j = 0
        for i in range(10):
            time.sleep(0.5)  # Simulate some delay for signal sampling
            cd.execute()
            data = cd.get_buffer().data(n=prediction_length, persistent=False)
            if data is not None:
                if len(list(data.values())) > 0  and len(list(data.values())[0]) >= prediction_length:
                    plt.clf()
                    plt.plot(range(j*n, j*n+n),list(lba_2.get_buffer().data().values())[0][j*n:j*n+n], alpha=0.5)
                    plt.plot(range(j*n+n, j*n+n+prediction_length),list(data.values())[0])
                    plt.pause(0.01)
                    j += 1
                
                assert type(data) == dict
                for key in data.keys():
                    assert type(data[key]) == list
                    if len(data[key]) > 0:
                        assert len(data[key]) == prediction_length


def test_regression_output_keys_match_length():
    """When output_keys length matches number of inputs, use provided keys for regression outputs."""
    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()

    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)

    prediction_length = 10
    custom_keys = ["rk0", "rk1"]

    rt = RegressionTransform(n=10, learning_required=False, min_inference_samples=20, persistent=False,
                             prediction_length=prediction_length, output_keys=custom_keys, model_name="Tirex")
    rt.install()
    rt.add_parent(lba)

    # accumulate at least 20 samples before checking output
    for _ in range(20):
        rt.execute()
        time.sleep(0.1)
    data = rt.get_buffer().data(n=prediction_length)
    # If there are two outputs, ensure our provided keys were used
    if len(data.keys()) == 2:
        assert set(data.keys()) == set(custom_keys)


def test_regression_output_keys_mismatch_uses_default():
    """When output_keys length mismatches, fall back to default naming for regression outputs."""
    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()

    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)

    prediction_length = 10
    custom_keys = ["only-one-key"]

    rt = RegressionTransform(n=10, learning_required=False, min_inference_samples=10, persistent=False,
                             prediction_length=prediction_length, output_keys=custom_keys, model_name="Tirex")
    rt.install()
    rt.add_parent(lba)

    # accumulate at least 10 samples before checking output
    for _ in range(15):
        rt.execute()
        time.sleep(0.05)
    data = rt.get_buffer().data(n=prediction_length)
    # Expect default naming pattern when input keys count != output_keys length
    # Default: ClassName-<FEATURE>-<i>
    if len(data.keys()) == 2:
        from pydag.agents.AgentKeywords import AgentKeywords
        expected = {
            RegressionTransform.cname() + "-" + AgentKeywords.FEATURE + "-" + "0",
            RegressionTransform.cname() + "-" + AgentKeywords.FEATURE + "-" + "1",
        }
        assert set(data.keys()) == expected
