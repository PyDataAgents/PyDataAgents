import time


from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.nodes.dataset.DatasetNames import DatasetNames
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.featureextraction.ROCKETExtractor import ROCKETExtractor


def test_010():
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    lba = LinkBufferAction()
    lba.buffer = sds
    lba.install()

    rocket = ROCKETExtractor(min_learning_samples=10, min_inference_samples=10, features_from_parent=["values"], persistent=False)
    rocket.install()
    rocket.add_parent(lba)

    n = 10

    for i in range(20):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        rocket.execute()
        data = rocket.buffer.data(n=10, persistent=False)
        assert type(data) == dict
        for key in data.keys():
            assert type(data[key]) == list
            if len(data[key]) > 0:
                time.sleep(0.1)
                #plt.plot(data[key])
                assert len(data[key]) == n
