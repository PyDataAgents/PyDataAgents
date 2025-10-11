import numpy as np
from sktime.datasets import load_UCR_UEA_dataset
import time
import matplotlib.pyplot as plt


from pydag.buffers.SampledBuffer import SampledBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.dataset.DatasetBuffer import DatasetBuffer


def test_000():
    
    X, y = load_UCR_UEA_dataset(name="Wine")
    
    d = X.to_dict(orient="list")
    
    li = np.array(list(d.values())).reshape(-1).tolist()
    print(li)
    

def test_010():

    n = 10
    sds = DatasetBuffer(dataset_name="Car", sort_by_y=True)
    sds.install()

    lba = LinkBufferAction()
    lba.buffer = sds


    
    for i in range(300):
        time.sleep(0.01)
        dsb = lba.buffer.data()
        if len(dsb.values()) > 0:
            print(dsb.values())
        if len(dsb.values()) > 0:
            assert len(dsb["values"]) >= n



def test_020():
    n = 10
    sds = DatasetBuffer(dataset_name="Car", sort_by_y=True)
    sds.install()

    lba = LinkBufferAction()
    lba.buffer = sds

    plt.plot(lba.buffer.data()["values"])
    plt.plot(lba.buffer.data()["y"])
    plt.show()
    
    for i in range(300):
        time.sleep(0.01)
        dsb = lba.buffer.data()
        if len(dsb.values()) > 0:
            print(dsb["y"])
        if len(dsb.values()) > 0:
            assert len(dsb["values"]) >= n


def test_030():
    # Test Dali CNC
    n = 10
    sds = DatasetBuffer(dataset_name="CNC", sort_by_y=True)
    sds.install()

    lba = LinkBufferAction()
    lba.buffer = sds

    plt.plot(lba.buffer.data()["values"])
    plt.plot(lba.buffer.data()["y"])
    plt.show()
    
    for i in range(300):
        time.sleep(0.01)
        dsb = lba.buffer.data()
        if len(dsb.values()) > 0:
            print(dsb["y"])
        if len(dsb.values()) > 0:
            assert len(dsb["values"]) >= n


def test_040():
    # Test CWRU
    n = 10
    sds = DatasetBuffer(dataset_name="CWRU", sort_by_y=True)
    sds.install()

    lba = LinkBufferAction()
    lba.buffer = sds
    dsb = lba.buffer.data(persistent=True)
    for d in dsb.values():
        if d != "y":
            plt.plot(d)
    plt.plot(dsb["y"])
    plt.show()
    