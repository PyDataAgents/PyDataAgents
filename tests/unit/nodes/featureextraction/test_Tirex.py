import time


from pydag.buffers.DatasetBuffer import DatasetBuffer, DatasetNames
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.nodes.featureextraction.TirexExtractor import TirexExtractor

def test_tirex_exec_produces_n_length():
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
        
    lba = LinkBufferAction()
    lba.set_buffer(sds)
    lba.install()

    rocket = TirexExtractor(min_learning_samples=10, min_inference_samples=10, input_keys=["values"], persistent=False)
    rocket.install()
    rocket.add_parent(lba)

    n = 10

    for i in range(10):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        rocket.execute()
        data = rocket.get_buffer().data(n=10, persistent=False)
        if data is not None:
            assert type(data) == dict
            for key in data.keys():
                assert type(data[key]) == list
                if len(data[key]) > 0:
                    assert len(data[key]) == n
