import numpy as np
from sktime.datasets import load_UCR_UEA_dataset
import time
import matplotlib.pyplot as plt


from pydag.buffers.SampledBuffer import SampledBuffer
from pydag.nodes.dataset.DatasetBuffer import DatasetBuffer
from pydag.nodes.dataset.DatasetBuffer import DatasetNames

def test_000():
    
    X, y = load_UCR_UEA_dataset(name="Wine")
    
    d = X.to_dict(orient="list")
    
    li = np.array(list(d.values())).reshape(-1).tolist()
    print(li)
    

def test_010():
    sampling_period = 100
    n = 10
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()

    sb = SampledBuffer(capacity=100000, signal=sds, sampling_period=sampling_period, n=n)
    sb.install()
    
    for i in range(10):
        time.sleep(1)
        dsb = sb.data()
        #plt.clf()
        #plt.plot(dsb["values"])
        #plt.pause(0.1)
        if len(dsb.values()) > 0:
            assert len(dsb["values"]) >= n
        print(dsb)
