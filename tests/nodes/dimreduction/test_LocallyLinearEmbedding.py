from sktime.datasets import load_airline
from sktime.forecasting.base import ForecastingHorizon
from sktime.split import temporal_train_test_split
import matplotlib.pyplot as plt
import time

from pydag.nodes.dimreduction.LocallyLinearEmbeddingsReduction import LocallyLinearEmbeddingsReduction
from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.nodes.dataset.DatasetNames import DatasetNames
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction

def test_000():

    dimensions = 3
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.buffer = sds
    lba.install()

    LLE = LocallyLinearEmbeddingsReduction(dimensions=dimensions, sample_length=10, min_learning_samples=10, min_inference_samples=1, persistent=False)
    LLE.install()

    LLE.add_parent(lba)
    
    n = 10

    for i in range(50):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        LLE.execute()
        data = LLE.buffer.data(n=10, persistent=False)
        assert type(data) == dict
        for key in data.keys():
            assert type(data[key]) == list
            if len(data[key]) > 0:
                time.sleep(0.1)
                #plt.clf()
                #plt.scatter(data[key][0], data[key][1])
                assert len(data[key]) == dimensions





def test_001():

    dimensions = 3
    features_from_parent = ["values"]
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.buffer = sds
    lba.install()

    LLE = LocallyLinearEmbeddingsReduction(dimensions=dimensions, sample_length=10, features_from_parent=["values"], min_learning_samples=10, min_inference_samples=1, persistent=False)
    LLE.install()

    LLE.add_parent(lba)
    
    n = 10

    for i in range(50):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        LLE.execute()
        data = LLE.buffer.data(n=10, persistent=False)
        assert type(data) == dict
        for key in data.keys():
            assert type(data[key]) == list
            if len(data[key]) > 0:
                time.sleep(0.1)
                #plt.clf()
                #plt.scatter(data[key][0], data[key][1])
                assert len(data[key]) == dimensions
                assert len(list(data.keys())) == len(features_from_parent)