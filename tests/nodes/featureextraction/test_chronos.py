import time


from pydag.nodes.featureextraction.ChronosExtractor import ChronosExtractor
from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.nodes.dataset.DatasetNames import DatasetNames
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.SignalBuffer import SignalBuffer


def test_000():

    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.buffer = sine_buff

    
    chronos = ChronosExtractor()
    chronos.install()

    chronos.add_parent(lba)

    for i in range(100):
        #time.sleep(0.5)
        chronos.execute()
        data = chronos.buffer.data(n=10)
        if len(data.values()) > 0:
            assert len(data[list(data.keys())[0]]) > 0 and len(data[list(data.keys())[0]]) <= 10, f"Data length out of bounds: {len(data[list(data.keys())[0]])}"



def test_010():
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.buffer = sds
    lba.install()

    chronos = ChronosExtractor(sample_length=10, persistent=False)
    chronos.install()

    chronos.add_parent(lba)
    
    n = 10

    for i in range(20):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        chronos.execute()
        data = chronos.buffer.data(n=10, persistent=False)
        assert type(data) == dict
        for key in data.keys():
            assert type(data[key]) == list
            if len(data[key]) > 0:
                #time.sleep(0.1)
                #plt.clf()
                #plt.plot(data[key])
                assert len(data[key]) == n


def test_020():

    # With data normalization
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.buffer = sds
    lba.install()

    chronos = ChronosExtractor(sample_length=10, persistent=False)
    chronos.install()

    chronos = ChronosExtractor(sample_length=10, min_inference_samples=10, persistent=False, normalize=True)
    chronos.install()

    chronos.add_parent(lba)
    
    n = 10

    for i in range(20):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        chronos.execute()
        data = chronos.buffer.data(n=10, persistent=False)
        assert type(data) == dict
        for key in data.keys():
            assert type(data[key]) == list
            if len(data[key]) > 0:
                #time.sleep(0.1)
                #plt.clf()
                #plt.plot(data[key])
                assert len(data[key]) == n
