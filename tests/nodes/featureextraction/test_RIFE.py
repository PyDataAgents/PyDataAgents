import time

from pydag.nodes.featureextraction.RIFEExtractor import RIFEExtractor
from pydag.nodes.dataset.DatasetBuffer import DatasetBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.SignalBuffer import SignalBuffer
import numpy as np
import matplotlib.pyplot as plt
from pydag.nodes.dimreduction.PCADimReduction import PCADimReduction
from pydag.agents.Agent import Agent
from pydag.services.statemachine.StatemachineService import StatemachineService
from pydag.services.statemachine.SimpleActionService import SimpleActionService
from pydag.services.rest.RestService import RestService

# The tests mirror those in test_PSD but adapted for 256 RIFE features and key naming (-feature-rife-<i>)


def test_000():
    # Single streaming sine signal; expect exactly 256 features when data available.
    signal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=signal, capacity=1000)
    sine_buff.install()
    lba = LinkBufferAction()
    lba.buffer = sine_buff

    rife = RIFEExtractor()
    rife.install()
    rife.add_parent(lba)

    for _ in range(10):
        time.sleep(0.5)
        rife.execute()
        data = rife.buffer.data(persistent=False)
        if data and len(data.values()) > 0:
            first_key = list(data.keys())[0]
            assert len(data[first_key]) == 256, f"Data length must be 256, but got: {len(data[first_key])}"
            for k, vec in data.items():
                assert all(x == 0 for x in vec), "All feature values must be zero for short input data"


def test_001():
    # Single streaming sine signal; expect exactly 256 features when data available. Test what happens with short input data with length 10.
    signal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=signal, capacity=1000)
    sine_buff.install()
    lba = LinkBufferAction()
    lba.buffer = sine_buff

    rife = RIFEExtractor(sample_length=10)
    rife.install()
    rife.add_parent(lba)

    for _ in range(50):
        time.sleep(0.5)
        rife.execute()
        data = rife.buffer.data(persistent=False)
        if data and len(data.values()) > 0:
            first_key = list(data.keys())[0]
            assert len(data[first_key]) == 320, f"Data length must be 320, but got: {len(data[first_key])}"
            for k, vec in data.items():
                assert all(x == 0 for x in vec[-5:]), "The last 5 features are 0 because the method zero-pads to 320 if not enough valid intervals are found."
                assert all(x != 0 for x in vec[:50]), "The first 50 features must be != 0."


def test_002():
    # Single streaming sine signal; expect exactly 256 features when data available. Test what happens with short input data with length 10 and multiple inference samples.
    signal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=signal, capacity=1000)
    sine_buff.install()
    lba = LinkBufferAction()
    lba.buffer = sine_buff

    rife = RIFEExtractor(sample_length=100, min_inference_samples=5)
    rife.install()
    rife.add_parent(lba)

    for _ in range(100):
        time.sleep(0.5)
        rife.execute()
        data = rife.buffer.data(persistent=False)
        if data and len(data.values()) > 0:
            first_key = list(data.keys())[0]
            assert len(data[first_key]) == 320*5, f"Data length must be 320, but got: {len(data[first_key])}"
            assert len(list(data.keys())) == 2, "Expected exactly two feature vector keys"
            for k, vec in data.items():
                assert all(x != 0 for x in vec[:50]), "The first 50 features must be != 0."



def test_010():
    # CWRU dataset; ensure feature vectors differ across iterations when signal changes.
    dataset_buffer = DatasetBuffer("CWRU", sort_by_y=True)
    dataset_buffer.install()
    lba = LinkBufferAction()
    lba.buffer = dataset_buffer

    rife = RIFEExtractor(sample_length=100, persistent=False)
    rife.install()
    rife.add_parent(lba)
    prev = None
    plt.ion()

    for _ in range(50):
        time.sleep(0.5)
        rife.execute()
        data = rife.buffer.data(persistent=False)
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


def test_020():
    # Multiple inference samples: accumulate 5*sample_length before inference if min_inference_samples=5.
    dataset_buffer = DatasetBuffer("CWRU", sort_by_y=True)
    dataset_buffer.install()
    lba = LinkBufferAction()
    lba.buffer = dataset_buffer

    rife = RIFEExtractor(sample_length=100, min_inference_samples=5, persistent=False)
    rife.install()
    rife.add_parent(lba)

    for _ in range(50):
        time.sleep(0.5)
        rife.execute()
        data = rife.buffer.data(persistent=False)
        if data and len(data.values()) > 0:
            first_key = list(data.keys())[0]
            # Expect a single 320*5-length feature vector per inference run
            assert len(data[first_key]) in (0, 320*5), f"Data length must be 320*5 or 0, but got: {len(data[first_key])}"



def test_030():
    
    ag = Agent()
        
    signal = DatasetBuffer(id="B1", dataset_name="CWRU", sort_by_y=True)    
    signal_2 = DatasetBuffer(id="B2", dataset_name="CWRU", sort_by_y=True)
    

    sm = SimpleActionService() 
     
    lba = LinkBufferAction()
    lba.buffer = signal

    lba_2 = LinkBufferAction()
    lba_2.buffer = signal_2

    rife = RIFEExtractor(id="R1", sample_length=100, min_inference_samples=5, persistent=False)
    rife.add_parent(lba)

    rs = RestService(port=8008)

    # Add buffers
    ag.add_buffer(signal)
    ag.add_buffer(signal_2) 


    # Add Nodes
    sm.add_node(lba)
    sm.add_node(lba_2)
    sm.add_node(rife)
    
    # Add Services
    ag.add_service(sm)
    ag.add_service(rs)
    
    # Start Agent
    ag.start_blocking()                                                                  





if __name__ == "__main__":
    # Uncomment individual tests for manual debugging
    #test_000()
    #test_001()
    #test_002()
    #test_010()
    #test_020()
    test_030()
    

