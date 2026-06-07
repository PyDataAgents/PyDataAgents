import time


from pydag.nodes.dimreduction.PCADimReduction import PCADimReduction
from pydag.buffers.DatasetBuffer import DatasetBuffer, DatasetNames
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.agents.AgentConfig import AgentConfig


def test_pca_exec_produces_dimensioned_output():

    dimensions = 3
    min_inference_samples = 1
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value, )
    sds.install()
    

    lba = LinkBufferAction()
    lba.set_buffer(sds)
    lba.install()

    PCA = PCADimReduction(dimensions=dimensions, sample_length=10, min_learning_samples=10, min_inference_samples=min_inference_samples, persistent=False, ignore_keys=["y"])
    PCA.install()

    PCA.add_parent(lba)
    
    n = 10

    for i in range(5):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        PCA.execute()
        data = PCA.get_buffer().data(n=10, persistent=False)
        if data is not None:
            assert type(data) == dict
            for key in data.keys():
                assert type(data[key]) == list
                if len(data[key]) > 0:
                    assert len(data[key]) == dimensions*min_inference_samples


def test_pca_exec_produces_dimensioned_output_repeat():

    dimensions = 3
    min_inference_samples = 1
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.set_buffer(sds)
    lba.install()

    PCA = PCADimReduction(dimensions=dimensions, sample_length=10, min_learning_samples=10, min_inference_samples=min_inference_samples, persistent=False, ignore_keys=["y"])
    PCA.install()

    PCA.add_parent(lba)
    
    n = 10

    for i in range(5):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        PCA.execute()
        data = PCA.get_buffer().data(n=10, persistent=False)
        if data is not None:
            assert type(data) == dict
            for key in data.keys():
                assert type(data[key]) == list
                if len(data[key]) > 0:
                    assert len(data[key]) == dimensions*min_inference_samples

def test_pca_sample_length_parameter_respected():

    dimensions = 3
    min_inference_samples = 1
    sample_length = 10
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.set_buffer(sds)
    lba.install()

    PCA = PCADimReduction(dimensions=dimensions, sample_length=sample_length, min_learning_samples=10, min_inference_samples=min_inference_samples, persistent=False, ignore_keys=["y"])
    PCA.install()

    PCA.add_parent(lba)
    
    n = 10

    for i in range(5):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        PCA.execute()
        data = PCA.get_buffer().data(n=10, persistent=False)
        if data is not None:
            assert type(data) == dict
            for key in data.keys():
                assert type(data[key]) == list
                if len(data[key]) > 0:
                    assert len(data[key]) == dimensions*min_inference_samples

def test_pca_input_keys_and_feature_count():

    dimensions = 3
    input_keys = ["values"]
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.set_buffer(sds)
    lba.install()

    PCA = PCADimReduction(dimensions=dimensions, sample_length=10, input_keys=input_keys, min_learning_samples=10, min_inference_samples=1, persistent=False, ignore_keys=["y"])
    PCA.install()

    PCA.add_parent(lba)
    
    n = 10

    for i in range(5):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        PCA.execute()
        data = PCA.get_buffer().data(n=10, persistent=False)
        if data is not None:
            for key in data.keys():
                assert type(data[key]) == list
                if len(data[key]) > 0:
                    assert len(data[key]) == dimensions 
                    assert len(list(data.keys())) == len(input_keys) +2 # Because of timestamps and indices
        else:
            continue
        # Ensure that finally data is exisiting and valid
        assert type(data) == dict
        for key in data.keys():
                assert type(data[key]) == list
                if len(data[key]) > 0:
                    assert len(data[key]) == dimensions
                    assert len(list(data.keys())) == len(input_keys) +2 # Because of timestamps and indices


def test_feature_key_naming_pattern():
    """Ensure returned feature keys follow the expected naming pattern
    `ClassName-<FEATURE><i>` and index matches enumeration order.
    """

    dimensions = 3

    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()

    lba = LinkBufferAction()
    lba.set_buffer(sds)
    lba.install()

    PCA = PCADimReduction(dimensions=dimensions, sample_length=10, min_learning_samples=10, min_inference_samples=1, persistent=False, ignore_keys=["y"])
    PCA.install()

    PCA.add_parent(lba)

    for _ in range(5):
        time.sleep(0.5)
        PCA.execute()
        data = PCA.get_buffer().data(n=10, persistent=False)
        if data:
            assert type(data) == dict
            for idx, k in enumerate(data.keys()):
                if k not in [AgentConfig.INDEX, AgentConfig.TIMESTAMPS]:
                    expected_key = PCADimReduction.__name__ + "-" + AgentConfig.FEATURE + "-" + f"{idx}"
                    assert k == expected_key