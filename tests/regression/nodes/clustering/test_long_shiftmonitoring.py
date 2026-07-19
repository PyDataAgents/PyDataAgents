import matplotlib.pyplot as plt
import time


from pydag.buffers.DictBuffer import DictBuffer
from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.nodes.featureextraction.ChronosExtractor import ChronosExtractor
from pydag.nodes.featureextraction.ROCKETExtractor import ROCKETExtractor
from pydag.nodes.clustering.ShiftMonitoring import ShiftMonitoring
from pydag.nodes.dimreduction.PCADimReduction import PCADimReduction
from pydag.services.statemachine.SimpleStatemachine import SimpleStatemachine
from pydag.agents.Agent import Agent
from pydag.nodes.featureextraction.PSDExtractor import PSDExtractor



def test_long_ecg5000_with_pca_feature_extraction():
    "Test Functionality on ECG5000 data with feature extraction."
    # ECG5000 Length for class 1: 400.000 Datapoints. Length for "one-sample" = 140 Points.
    # Car Length for class 1: 10.000 Datapoints. Length for "one-sample" = 577 Points.
    # ChlorineConcentration Length for class 1: 166500 Datapoints. Length for "one-sample" = 166 Points.
    

    signal = DatasetBuffer(dataset_name="ECG5000", sort_by_y=True)
    signal.install()

    signal_2 = DatasetBuffer(dataset_name="ECG5000", sort_by_y=True)
    signal_2.install()
    
    lba = LinkBufferAction()
    lba.set_buffer(signal)

    lba_2 = LinkBufferAction()
    lba_2.set_buffer(signal_2)

    chronos = ChronosExtractor(sample_length=140, persistent=False, normalize=True, input_keys=["values"]) 
    chronos.install()
    chronos.add_parent(lba)

    pca = PCADimReduction(dimensions=2, min_learning_samples=400, sample_length=384, min_inference_samples=1,normalize=True, input_keys=["values-feature-amazon-chronos-bolt-mini-0"], persistent=False) #384
    pca.install()
    pca.add_parent(chronos) # Rad data is passed to PCA directly to have a more direct connection between input data and PCA output.

    shift = ShiftMonitoring(min_learning_samples=2000, sample_length=2, min_inference_samples=1, persistent=False, input_keys=["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"], return_input=True, sensitivity=2) #1800
    shift.install()
    shift.add_parent(pca)

    fig, ax = plt.subplots(2,1)
    #plt.ion()
    for i in range(5000):
        time.sleep(0.1)
        chronos.execute()
        pca.execute()
        shift.execute()
        data = shift.get_buffer().data(persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        data_2 = lba_2.get_buffer().data(n=140, persistent=False)
        print(data)
        if hasattr(data, "values") and len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data['values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift'])) == 1
                assert len(list(data.values())) == 6 # Input data is returned in this test. 
                
                if data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift"] == 5.407847548518865e-05:
                    assert data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"] == 1, f"At value 5.407847548518865e-05 a shift should be detected but {data['values-feature-decision'][0]} was detected."
                if data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift"] == 3.308598942337312e-06:
                    assert data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"] == 1, f"At value 3.308598942337312e-06 a shift should be detected but {data['values-feature-decision'][0]} was detected."


        if hasattr(data, "values") and len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                
                # Groundtruth Color
                if data_2["y"][0]== 1:
                    g_color = 'g'
                else:
                    g_color = 'r'
                
                # Prediction Color
                if data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"][0] == 0:
                    color = 'g'
                elif data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"][0] == None:
                    color = 'b'
                else:
                    color = 'r'
                #ax[2].scatter(data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][0], data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][1], color=color)
                #plt.pause(0.05)
                ax[0].scatter(data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-0"][-1], data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-1"][-1], color=color)
                ax[0].set_title("Prediction")
                ax[1].scatter(data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-0"][-1], data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-1"][-1], color=g_color)
                ax[1].set_title("Groundtruth")
            if i % 10 == 0:
                fig.savefig(f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs/shiftmonitoring_test007_plot_iteration{i}.png")



def test_long_ecg5000_with_rocket_feature_extraction():
    "Test Functionality on ECG5000 data with ROCKET feature extraction."
    # ECG5000 Length for class 1: 400.000 Datapoints. Length for "one-sample" = 140 Points.
    # Car Length for class 1: 10.000 Datapoints. Length for "one-sample" = 577 Points.
    # ChlorineConcentration Length for class 1: 166500 Datapoints. Length for "one-sample" = 166 Points.
    
    

    signal = DatasetBuffer(dataset_name="ECG5000", sort_by_y=True)
    signal.install()

    signal_2 = DatasetBuffer(dataset_name="ECG5000", sort_by_y=True)
    signal_2.install()
    
    lba = LinkBufferAction()
    lba.set_buffer(signal)

    lba_2 = LinkBufferAction()
    lba_2.set_buffer(signal_2)

    #chronos = ChronosExtractor(sample_length=140, persistent=False, normalize=True, input_keys=["values"]) 
    rocket = ROCKETExtractor(sample_length=140, persistent=False, normalize=True, input_keys=["values"])
    rocket.install()
    rocket.add_parent(lba)

    pca = PCADimReduction(dimensions=2, min_learning_samples=600, sample_length=20000, min_inference_samples=1,normalize=True, input_keys=["values-feature-ROCKET-0"], persistent=False) #400
    pca.install()
    pca.add_parent(rocket) # Rad data is passed to PCA directly to have a more direct connection between input data and PCA output.

    shift = ShiftMonitoring(min_learning_samples=2000, sample_length=2, min_inference_samples=1, persistent=False, input_keys=["values-feature-ROCKET-0-feature-PCA"], return_input=True, sensitivity=2) #2000
    shift.install()
    shift.add_parent(pca)

    fig, ax = plt.subplots(2,1)
    #plt.ion()
    for i in range(5000):
        #time.sleep(0.1)
        rocket.execute()
        pca.execute()
        shift.execute()
        data = shift.get_buffer().data(persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        data_2 = lba_2.get_buffer().data(n=140, persistent=False)
        print(data)
        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data['values-feature-ROCKET-0-feature-PCA-feature-shift'])[0]) == 1
                assert len(list(data.values())) == 5 # Input data is returned in this test. 
                """
                if data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift"][0] == 5.407847548518865e-05:
                    assert data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"][0] == 1, f"At value 5.407847548518865e-05 a shift should be detected but {data['values-feature-decision'][0]} was detected."
                if data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift"][0] == 3.308598942337312e-06:
                    assert data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"][0] == 1, f"At value 3.308598942337312e-06 a shift should be detected but {data['values-feature-decision'][0]} was detected."
                """

        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                
                # Groundtruth Color
                if data_2["y"][0]== 1:
                    g_color = 'g'
                else:
                    g_color = 'r'
                
                # Prediction Color
                if data["values-feature-ROCKET-0-feature-PCA-feature-decision"][0] == 0:
                    color = 'g'
                elif data["values-feature-ROCKET-0-feature-PCA-feature-decision"][0] == None:
                    color = 'b'
                else:
                    color = 'r'
                #ax[2].scatter(data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][0], data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][1], color=color)
                #plt.pause(0.05)
                ax[0].scatter(data["values-feature-ROCKET-0-feature-PCA-0"][-1], data["values-feature-ROCKET-0-feature-PCA-1"][-1], color=color)
                ax[0].set_title("Prediction")
                ax[1].scatter(data["values-feature-ROCKET-0-feature-PCA-0"][-1], data["values-feature-ROCKET-0-feature-PCA-1"][-1], color=g_color)
                ax[1].set_title("Groundtruth")
            if i % 10 == 0:
                fig.savefig(f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs/shiftmonitoring_test007_plot_iteration{i}.png")



def test_long_bosch_cnc_without_feature_extraction():
    "Long Time Test Functionality on one feature of BOSCH CNC  data WITHOUT feature extraction."
    # ECG5000 Length for class 1: 400.000 Datapoints. Length for "one-sample" = 140 Points.
    # Car Length for class 1: 10.000 Datapoints. Length for "one-sample" = 577 Points.
    # Wafer Length for class 1: 100.000 Datapoints. Length for "one-sample" = 152 Points.
    # ChlorineConcentration Length for class 1: 166500 Datapoints. Length for "one-sample" = 166 Points.
    # Bosch CNC Length for class 1: 7768848 Datapoints. Length for "one-sample" = 500 Points.
    

    signal = DatasetBuffer(dataset_name="CNC", sort_by_y=True)
    signal.install()

    signal_2 = DatasetBuffer(dataset_name="CNC", sort_by_y=True)
    signal_2.install()
    
    lba = LinkBufferAction()
    lba.set_buffer(signal)

    lba_2 = LinkBufferAction()
    lba_2.set_buffer(signal_2)

    chronos = ChronosExtractor(sample_length=500, persistent=False, normalize=True, input_keys=["values_0"]) 
    #rocket = ROCKETExtractor(sample_length=500, persistent=False, normalize=True, input_keys=["values"])
    chronos.install()
    chronos.add_parent(lba)

    pca = PCADimReduction(dimensions=2, min_learning_samples=200, sample_length=500, min_inference_samples=1,normalize=True, input_keys=["values_0"], persistent=False) #400
    pca.install()
    pca.add_parent(lba) 
    shift = ShiftMonitoring(min_learning_samples=1200, sample_length=2, min_inference_samples=1, persistent=False, input_keys=["values_0-feature-PCA"], return_input=True, sensitivity=2) #2000
    shift.install()
    shift.add_parent(pca)

    fig, ax = plt.subplots(2,1)
    #plt.ion()
    for i in range(50000):
        #time.sleep(0.1)
        #chronos.execute()
        pca.execute()
        shift.execute()
        data = shift.get_buffer().data(persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        data_2 = lba_2.get_buffer().data(n=500, persistent=False)
        print(data)
        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data['values_0-feature-PCA-feature-shift'])[0]) == 1
                assert len(list(data.values())) == 5 # Input data is returned in this test. 
                """
                if data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift"][0] == 5.407847548518865e-05:
                    assert data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"][0] == 1, f"At value 5.407847548518865e-05 a shift should be detected but {data['values-feature-decision'][0]} was detected."
                if data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift"][0] == 3.308598942337312e-06:
                    assert data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"][0] == 1, f"At value 3.308598942337312e-06 a shift should be detected but {data['values-feature-decision'][0]} was detected."
                """

        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                
                # Groundtruth Color
                if data_2["y"][0]== 0:
                    g_color = 'g'
                else:
                    g_color = 'r'
                
                # Prediction Color
                if data["values_0-feature-PCA-feature-decision"][0] == 0:
                    color = 'g'
                elif data["values_0-feature-PCA-feature-decision"][0] == None:
                    color = 'b'
                else:
                    color = 'r'
                #ax[2].scatter(data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][0], data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][1], color=color)
                #plt.pause(0.05)
                ax[0].scatter(data["values_0-feature-PCA-0"][-1], data["values_0-feature-PCA-1"][-1], color=color)
                ax[0].set_title("Prediction")
                ax[1].scatter(data["values_0-feature-PCA-0"][-1], data["values_0-feature-PCA-1"][-1], color=g_color)
                ax[1].set_title("Groundtruth")
            if i % 10 == 0:
                fig.savefig(f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs/shiftmonitoring_test007_plot_iteration{i}.png")




def test_long_cwru_with_feature_extraction():
    "Long Time Test Functionality on one feature of CWRU data with feature extraction."
    # ECG5000 Length for class 1: 400.000 Datapoints. Length for "one-sample" = 140 Points.
    # Car Length for class 1: 10.000 Datapoints. Length for "one-sample" = 577 Points.
    # Wafer Length for class 1: 100.000 Datapoints. Length for "one-sample" = 152 Points.
    # ChlorineConcentration Length for class 1: 166500 Datapoints. Length for "one-sample" = 166 Points.
    # Bosch CNC Length for class 1: 7768848 Datapoints. Length for "one-sample" = 500 Points.
    # CWRU Length for class 1: 122136 Datapoints. Length for "one-sample" = 500 Points.
    

    signal = DatasetBuffer(dataset_name="CWRU", sort_by_y=True)
    signal.install()

    signal_2 = DatasetBuffer(dataset_name="CWRU", sort_by_y=True)
    signal_2.install()
    
    lba = LinkBufferAction()
    lba.set_buffer(signal)

    lba_2 = LinkBufferAction()
    lba_2.set_buffer(signal_2)

    chronos = ChronosExtractor(sample_length=100, persistent=False, normalize=True, input_keys=["values_0"]) 
    #rocket = ROCKETExtractor(sample_length=500, persistent=False, normalize=True, input_keys=["values"])
    chronos.install()
    chronos.add_parent(lba)

    pca = PCADimReduction(dimensions=2, min_learning_samples=400, sample_length=384, min_inference_samples=1,normalize=True, input_keys=["values_0-feature-amazon-chronos-bolt-mini-0"], persistent=False) #400
    pca.install()
    pca.add_parent(chronos) 
    shift = ShiftMonitoring(min_learning_samples=600, sample_length=2, min_inference_samples=1, persistent=False, input_keys=["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA"], return_input=True, sensitivity=2) #2000
    shift.install()
    shift.add_parent(pca)

    fig, ax = plt.subplots(2,1)
    #plt.ion()
    for i in range(50000):
        #time.sleep(0.1)
        chronos.execute()
        pca.execute()
        shift.execute()
        data = shift.get_buffer().data(persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        data_2 = lba_2.get_buffer().data(n=100, persistent=False)
        print(data)
        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data['values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift'])[0]) == 1
                assert len(list(data.values())) == 5 # Input data is returned in this test. 
                """
                if data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift"][0] == 5.407847548518865e-05:
                    assert data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"][0] == 1, f"At value 5.407847548518865e-05 a shift should be detected but {data['values_0-feature-decision'][0]} was detected."
                if data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift"][0] == 3.308598942337312e-06:
                    assert data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"][0] == 1, f"At value 3.308598942337312e-06 a shift should be detected but {data['values_0-feature-decision'][0]} was detected."
                """

        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                
                # Groundtruth Color
                if data_2["y"][0]== 0:
                    g_color = 'g'
                else:
                    g_color = 'r'
                
                # Prediction Color
                if data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"][0] == 0:
                    color = 'g'
                elif data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"][0] == None:
                    color = 'b'
                else:
                    color = 'r'
                #ax[2].scatter(data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][0], data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][1], color=color)
                #plt.pause(0.05)
                ax[0].scatter(data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA-0"][-1], data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA-1"][-1], color=color)
                ax[0].set_title("Prediction")
                ax[1].scatter(data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA-0"][-1], data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA-1"][-1], color=g_color)
                ax[1].set_title("Groundtruth")
            if i % 10 == 0:
                fig.savefig(f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs/shiftmonitoring_test007_plot_iteration{i}.png")


def test_long_agent_mode_with_rest_api():

    # Test Distribution Shift Monitoring in Agent mode with REST-API
    
    ag = Agent()
    
    signal = DatasetBuffer(id="signal", dataset_name="ChlorineConcentration", sort_by_y=True, index_enabled=True, duplicate_ids=["ChlorineConcentration_2"])
    # 903 + x datapoints with length 166 belong to category 1. 
    signal.install(ag) # Required to create duplicates since they are created during installation.

    index_buff = DictBuffer(id="index_buffer", capacity=1)
    _index = signal.data(persistent=True)["index"][-1]
    index_buff.push({"count": _index})

    sm = SimpleStatemachine() 
     
    lba = LinkBufferAction()
    lba.set_buffer(signal)

    lba_raw = LinkBufferAction(id="lba_raw")
    lba_raw.set_buffer(signal.get_duplicates()["ChlorineConcentration_2"])

    extractor = PSDExtractor(id="PSD", sample_length=166, persistent=False, normalize=True, input_keys=["values"])
    extractor.add_parent(lba)
    
    pca = PCADimReduction(id="PCA", dimensions=2, min_learning_samples=10, sample_length=261, min_inference_samples=1,normalize=True, input_keys=["PSDExtractor-feature-0"], persistent=False)
    pca.add_parent(extractor)
    
    shift_buf = DictBuffer(id="shift_buffer", capacity=1000, index_enabled=True)
    shift_buf.install(ag)
    
    sm_node = ShiftMonitoring(id="shiftmonitoring_node", min_learning_samples=703, sample_length=2, min_inference_samples=1, persistent=False, return_input=True)
    sm_node.set_buffer(shift_buf)
    sm_node.add_parent(pca)

    # Add buffers
    ag.add_buffer(signal)
    ag.add_buffer(index_buff)
    ag.add_buffer(shift_buf)

    # Add Nodes
    sm.add_node(lba)
    sm.add_node(lba_raw)
    sm.add_node(extractor)
    sm.add_node(pca)
    sm.add_node(sm_node)
    
    # Add Services
    ag.add_service(sm)
    
    # Start Agent
    ag.release()   