import matplotlib.pyplot as plt
import time


from pydag.nodes.regression.RegressionTransform import RegressionTransform
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction


def test_000():
    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.buffer = sine_buff

    prediction_length = 10

    cd = RegressionTransform(n=10, learning_required=False, min_inference_samples=20, persistent=False, prediction_length=prediction_length)
    cd.install()
    cd.add_parent(lba)

    for i in range(10):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        cd.execute()
        data = cd.buffer.data(n=prediction_length)
        print(data)
        assert type(data) == dict
        for key in data.keys():
            assert type(data[key]) == list
            if len(data[key]) > 0:
                assert len(data[key]) == prediction_length

def test_001():
    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()




    for i in range(10):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        data = sine_buff.data(n=100)
        print(data)
        if len(list(data.values())[0]) > 0:
            assert len(list(data.values())[0]) <= 100, f"Data length exceeded: {len(list(data.values())[0])}"



def test_002():
    for name in ["CHRONOS", "Tirex"]:
        singal = Sine(f=1, a=1, p=0, n=0.1)
        sine_buff = SignalBuffer(signal=singal, capacity=1000)
        sine_buff_2 = SignalBuffer(signal=singal, capacity=1000)
        sine_buff.install()
        sine_buff_2.install()

        lba = LinkBufferAction()
        lba.buffer = sine_buff

        lba_2 = LinkBufferAction()
        lba_2.buffer = sine_buff_2

        prediction_length = 30
        n= 100

        cd = RegressionTransform(model_name= name, n=n, learning_required=False, min_inference_samples=n, persistent=False, prediction_length=prediction_length)
        cd.install()
        cd.add_parent(lba)
        j = 0
        for i in range(20):
            time.sleep(0.5)  # Simulate some delay for signal sampling
            cd.execute()
            data = cd.buffer.data(n=prediction_length, persistent=False)
            
            if len(list(data.values())) > 0  and len(list(data.values())[0]) >= prediction_length:
                plt.clf()
                plt.plot(range(j*n, j*n+n),list(lba_2.buffer.data().values())[0][j*n:j*n+n], alpha=0.5)
                plt.plot(range(j*n+n, j*n+n+prediction_length),list(data.values())[0])
                plt.pause(0.01)
                j += 1
            
            assert type(data) == dict
            for key in data.keys():
                assert type(data[key]) == list
                if len(data[key]) > 0:
                    assert len(data[key]) == prediction_length