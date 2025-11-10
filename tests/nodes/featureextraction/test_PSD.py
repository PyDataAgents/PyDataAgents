import time
import matplotlib.pyplot as plt


from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.nodes.featureextraction.PSDExtractor import PSDExtractor


# Test one inference sample as well as multiple inference samples on different datasets.

def test_000():
    # Test if always 257 values are returned
    signal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=signal, capacity=1000)
    sine_buff.install()
    lba = LinkBufferAction()
    lba.buffer = sine_buff

    PSD = PSDExtractor()
    PSD.install()
    PSD.add_parent(lba)

    for i in range(5):
        print(i)
        time.sleep(0.5)
        PSD.execute()
        data = PSD.buffer.data(persistent=False)
        if len(data.values()) > 0:
            assert len(data[list(data.keys())[0]]) == 257, f"Data length must be 257, but got: {len(data[list(data.keys())[0]])}"


def test_010():
    # Test if always 257 values are returned with a samople length of 100 and the signal is not changing
    signal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=signal, capacity=10**12)
    sine_buff.install()
    lba = LinkBufferAction()
    lba.buffer = sine_buff
    signal = None

    PSD = PSDExtractor(sample_length=100, persistent=True)
    PSD.install()
    PSD.add_parent(lba)
    #plt.ion()
    for i in range(50):
        print(i)
        time.sleep(0.5)
        PSD.execute()
        data = PSD.buffer.data(persistent=False)
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


def test_020():
    # Test if always 257 values are returned for UCR Dataset
    dataset_buffer = DatasetBuffer("Wine", sort_by_y=True)
    dataset_buffer.install()
    lba = LinkBufferAction()
    lba.buffer = dataset_buffer

    PSD = PSDExtractor(sample_length=100, persistent=False)
    PSD.install()
    PSD.add_parent(lba)
    #plt.ion()
    for i in range(50):
        print(i)
        time.sleep(0.5)
        PSD.execute()
        data = PSD.buffer.data(persistent=False)
        if data and len(data.values()) > 0:
            assert any([len(data[list(data.keys())[0]]) == 257, len(data[list(data.keys())[0]]) == 0]), f"Data length must be 257 or 0, but got: {len(data[list(data.keys())[0]])}"
            assert len(list(data.keys())) == 2
            assert all([key in data.keys() for key in ["values-feature-welch-0","y-feature-welch-1"]]), f"Keys must be ['values-feature-welch-0','y-feature-welch-1'], but got: {list(data.keys())}"
            #plt.plot(data[list(data.keys())[0]])
            #plt.pause(0.1)

def test_030():
    # Test if always 257 values are returned for CWRU data and signal is changing
    dataset_buffer = DatasetBuffer("CWRU", sort_by_y=True)
    dataset_buffer.install()
    lba = LinkBufferAction()
    lba.buffer = dataset_buffer
    signal = None
    PSD = PSDExtractor(sample_length=100, persistent=False)
    PSD.install()
    PSD.add_parent(lba)
    #plt.ion()
    for i in range(50):
        print(i)
        time.sleep(0.5)
        PSD.execute()
        data = PSD.buffer.data(persistent=False)
        if data and len(data.values()) > 0:
            assert any([len(data[list(data.keys())[0]]) == 257, len(data[list(data.keys())[0]]) == 0]), f"Data length must be 257 or 0, but got: {len(data[list(data.keys())[0]])}"
            assert len(list(data.keys())) == 2
            assert all([key in data.keys() for key in ["values-feature-welch-0","y-feature-welch-1"]]), f"Keys must be ['values-feature-welch-0','y-feature-welch-1'], but got: {list(data.keys())}"
            if len(data[list(data.keys())[0]]) == 257:
                if signal is None:
                    signal = data[list(data.keys())[0]]
                else:
                    assert signal != data[list(data.keys())[0]], "Signal must be different in each iteration, since the data is changing"
                    signal = data[list(data.keys())[0]]
            #plt.plot(data[list(data.keys())[0]])
            #plt.pause(0.1)


def test_040():
    # Test if always 257*5 values are returned for CWRU data and signal is changing when 5 inference samples are used
    dataset_buffer = DatasetBuffer("CWRU", sort_by_y=True)
    dataset_buffer.install()
    lba = LinkBufferAction()
    lba.buffer = dataset_buffer
    signal = None
    PSD = PSDExtractor(sample_length=100, min_inference_samples=5, persistent=False)
    PSD.install()
    PSD.add_parent(lba)
    #plt.ion()
    for i in range(50):
        print(i)
        time.sleep(0.5)
        PSD.execute()
        data = PSD.buffer.data(persistent=False)
        if data and len(data.values()) > 0:
            assert any([len(data[list(data.keys())[0]]) == 257*5, len(data[list(data.keys())[0]]) == 0]), f"Data length must be 257 or 0, but got: {len(data[list(data.keys())[0]])}"
            assert len(list(data.keys())) == 2
            assert all([key in data.keys() for key in ["values-feature-welch-0","y-feature-welch-1"]]), f"Keys must be ['values-feature-welch-0','y-feature-welch-1'], but got: {list(data.keys())}"
            if len(data[list(data.keys())[0]]) == 257*5:
                if signal is None:
                    signal = data[list(data.keys())[0]]
                else:
                    assert signal != data[list(data.keys())[0]], "Signal must be different in each iteration, since the data is changing"
                    signal = data[list(data.keys())[0]]
            #plt.plot(data[list(data.keys())[0]])
            #plt.pause(0.1)


if __name__ == "__main__":
    #test_000()
    #test_010()
    #test_020()
    #test_030()
    test_040()