import time


from pydag.nodes.dimreduction.PCADimReduction import PCADimReduction
from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.nodes.dataset.DatasetNames import DatasetNames
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction


def test_000():

    dimensions = 3
    min_inference_samples = 1
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value, )
    sds.install()
    

    lba = LinkBufferAction()
    lba.buffer = sds
    lba.install()

    PCA = PCADimReduction(dimensions=dimensions, sample_length=10, min_learning_samples=10, min_inference_samples=min_inference_samples, persistent=False)
    PCA.install()

    PCA.add_parent(lba)
    
    n = 10

    for i in range(50):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        PCA.execute()
        data = PCA.buffer.data(n=10, persistent=False)
        assert type(data) == dict
        for key in data.keys():
            assert type(data[key]) == list
            if len(data[key]) > 0:
                time.sleep(0.1)
                #plt.clf()
                #plt.scatter(data[key][0], data[key][1])
                assert len(data[key]) == dimensions*min_inference_samples


def test_001():

    dimensions = 3
    min_inference_samples = 1
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.buffer = sds
    lba.install()

    PCA = PCADimReduction(dimensions=dimensions, sample_length=10, min_learning_samples=10, min_inference_samples=min_inference_samples, persistent=False)
    PCA.install()

    PCA.add_parent(lba)
    
    n = 10

    for i in range(50):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        PCA.execute()
        data = PCA.buffer.data(n=10, persistent=False)
        assert type(data) == dict
        for key in data.keys():
            assert type(data[key]) == list
            if len(data[key]) > 0:
                time.sleep(0.1)
                #plt.clf()
                #plt.scatter(data[key][0], data[key][1])
                assert len(data[key]) == dimensions*min_inference_samples

def test_002():

    dimensions = 3
    min_inference_samples = 1
    sample_length = 10
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.buffer = sds
    lba.install()

    PCA = PCADimReduction(dimensions=dimensions, sample_length=sample_length, min_learning_samples=10, min_inference_samples=min_inference_samples, persistent=False)
    PCA.install()

    PCA.add_parent(lba)
    
    n = 10

    for i in range(50):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        PCA.execute()
        data = PCA.buffer.data(n=10, persistent=False)
        assert type(data) == dict
        for key in data.keys():
            assert type(data[key]) == list
            if len(data[key]) > 0:
                time.sleep(0.1)
                #plt.clf()
                #plt.scatter(data[key][0], data[key][1])
                assert len(data[key]) == dimensions*min_inference_samples

def test_003():

    dimensions = 3
    features_from_parent = ["values"]
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.buffer = sds
    lba.install()

    PCA = PCADimReduction(dimensions=dimensions, sample_length=10, features_from_parent=["values"], min_learning_samples=10, min_inference_samples=1, persistent=False)
    PCA.install()

    PCA.add_parent(lba)
    
    n = 10

    for i in range(50):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        PCA.execute()
        data = PCA.buffer.data(n=10, persistent=False)
        assert type(data) == dict
        for key in data.keys():
            assert type(data[key]) == list
            if len(data[key]) > 0:
                time.sleep(0.1)
                #plt.clf()
                #plt.scatter(data[key][0], data[key][1])
                assert len(data[key]) == dimensions
                assert len(list(data.keys())) == len(features_from_parent)