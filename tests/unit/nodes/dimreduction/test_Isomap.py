import time


from pydag.nodes.dimreduction.IsomapDimReduction import IsomapDimReduction
from pydag.agents.AgentKeywords import AgentKeywords
from pydag.buffers.DatasetBuffer import DatasetBuffer, DatasetNames
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction


def test_isomap_exec_produces_dimensioned_output():

    dimensions = 3
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.set_buffer(sds)
    lba.install()

    ISO = IsomapDimReduction(dimensions=dimensions, sample_length=10, min_learning_samples=10, min_inference_samples=1, persistent=False, ignore_keys=["y"])
    ISO.install()

    ISO.add_parent(lba)
    
    n = 10

    for i in range(5):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        ISO.execute() # TODO execute goes wrong please debug
        data = ISO.get_buffer().data(n=10, persistent=False)
        if data is not None:
            assert type(data) == dict
            for key in data.keys():
                assert type(data[key]) == list
                if len(data[key]) > 0:
                    time.sleep(0.1)
                    #plt.clf()
                    #plt.scatter(data[key][0], data[key][1])
                    assert len(data[key]) == dimensions




def test_isomap_input_keys_dimensioned_output():

    dimensions = 3
    
    
    sds = DatasetBuffer(dataset_name=DatasetNames.Wine.value)
    sds.install()
    
    
    lba = LinkBufferAction()
    lba.set_buffer(sds)
    lba.install()
    
    ISO = IsomapDimReduction(dimensions=dimensions, sample_length=10, input_keys=["values"], min_learning_samples=10, min_inference_samples=1, persistent=False, ignore_keys=["y"])
    ISO.install()

    ISO.add_parent(lba)
    
    n = 10

    for i in range(5):
        time.sleep(0.5)  # Simulate some delay for signal sampling
        ISO.execute()
        data = ISO.get_buffer().data(n=10, persistent=False)
        if data is not None:
            assert type(data) == dict
            for key in data.keys():
                assert type(data[key]) == list
                if len(data[key]) > 0:
                    assert len(data[key]) == dimensions


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

    ISO = IsomapDimReduction(dimensions=dimensions, sample_length=10, min_learning_samples=10, min_inference_samples=1, persistent=False, ignore_keys=["y"])
    ISO.install()

    ISO.add_parent(lba)

    for _ in range(5):
        time.sleep(0.5)
        ISO.execute()
        data = ISO.get_buffer().data(n=10, persistent=False)
        if data:
            assert type(data) == dict
            for idx, k in enumerate(data.keys()):
                if k not in [AgentKeywords.INDEX, AgentKeywords.TIMESTAMPS]:
                    expected_key = IsomapDimReduction.__name__ + "-" + AgentKeywords.FEATURE + "-" + f"{idx}"
                    assert k == expected_key