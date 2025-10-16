from sktime.datasets import load_airline
from sktime.forecasting.base import ForecastingHorizon
from sktime.split import temporal_train_test_split
import matplotlib.pyplot as plt
import time
import numpy as np


from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.signals.SampledSignal import SampledSignal
from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.nodes.featureextraction.ChronosExtractor import ChronosExtractor
from pydag.nodes.featureextraction.ROCKETExtractor import ROCKETExtractor
from pydag.nodes.clustering.ShiftMonitoring import ShiftMonitoring
from pydag.nodes.dimreduction.PCADimReduction import PCADimReduction
from pydag.services.rest.RestService import RestService
from pydag.services.statemachine.SimpleActionService import SimpleActionService
from pydag.agents.Agent import Agent


def test_000():

    n = 2

    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.buffer = sine_buff

    
    chronos = ChronosExtractor()
    chronos.install()
    chronos.add_parent(lba)

    pca = PCADimReduction(dimensions=2, min_learning_samples=10, sample_length=4, min_inference_samples=1, features_from_parent=["values-feature-amazon-chronos-bolt-mini-0"], persistent=False)
    pca.install()
    pca.add_parent(chronos)

    for i in range(20):
        time.sleep(0.1)
        chronos.execute()
        pca.execute()
        data = pca.buffer.data(n=n, persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        print(data)
        
        if len(data.values()) > 0:
            assert len(data[list(data.keys())[0]]) > 0 and len(data[list(data.keys())[0]]) == n, f"Data length out of bounds: {len(data[list(data.keys())[0]])}"



def test_001():
    "Test Basic Functionality on Sine Data as well as Plotting"
    n = 2

    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.buffer = sine_buff

    
    chronos = ChronosExtractor()
    chronos.install()
    chronos.add_parent(lba)

    pca = PCADimReduction(dimensions=2, min_learning_samples=10, sample_length=10, min_inference_samples=1, features_from_parent=["values-feature-amazon-chronos-bolt-mini-0"], persistent=False)
    pca.install()
    pca.add_parent(chronos)


    shift = ShiftMonitoring(min_learning_samples=10, sample_length=2, min_inference_samples=1, persistent=False, plot_folder=f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs", plot_on=True)
    shift.install()
    shift.add_parent(pca)

    for i in range(100):
        time.sleep(0.5)
        chronos.execute()
        pca.execute()
        shift.execute()
        data = shift.buffer.data(persistent=True) # We extract the last two samples
        print(data)


def test_002():
    "Test Basic Functionality on Raw Sine Data (Without Feature Extraction and Dimensionality Reduction) as well as Plotting"
    n = 2

    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.buffer = sine_buff

    

    shift = ShiftMonitoring(min_learning_samples=10, sample_length=4, min_inference_samples=1, persistent=False, plot_folder=f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs", plot_on=True)
    shift.install()
    shift.add_parent(lba)

    for i in range(50):
        time.sleep(0.5)
        shift.execute()
        data = shift.buffer.data(persistent=False) # We extract the last two samples
        print(data)
        if len(data.values()) > 0:
            assert len(list(data.values())[0]) == 1 # Always one value is returned
            assert len(list(data.values())) == 2 # Signal buffer returns two keys: values and timestamps and for each key one value is returned



def test_003():
    "Test 002 but with more inference samples."
    n = 2

    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.buffer = sine_buff

    

    shift = ShiftMonitoring(min_learning_samples=10, sample_length=3, min_inference_samples=5, persistent=False, plot_folder=f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs", plot_on=True)
    shift.install()
    shift.add_parent(lba)

    for i in range(100):
        time.sleep(0.5)
        shift.execute()
        data = shift.buffer.data(persistent=False)
        print(i)
        print(data)
        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data.values())) == 2 # Signal buffer returns two keys: values and timestamps and for each key one value is returned


def test_004():
    "Test Basic Functionality on Raw Sine Data (Without Feature Extraction and Dimensionality Reduction) as well as Plotting and return input data as well"
    sample_length = 2

    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.buffer = sine_buff

    

    shift = ShiftMonitoring(min_learning_samples=10, sample_length=sample_length, min_inference_samples=1, persistent=False, plot_folder=f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs", plot_on=True, return_input=True)
    shift.install()
    shift.add_parent(lba)

    for i in range(100):
        time.sleep(0.5)
        shift.execute()
        data = shift.buffer.data(persistent=False) # We extract the last two samples
        print(data)
        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data["values"])) == 1 
                assert len(list(data["values"])[0]) == 2
                assert len(list(data.values())) == 4 # Signal buffer returns two keys: values and timestamps and for each key one value is returned



def test_005():
    "Test Basic Functionality on Raw Sine Data (Without Feature Extraction and Dimensionality Reduction) as well as Plotting and return input data as well for multiple inference samples"
    sample_length = 2

    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.buffer = sine_buff

    

    shift = ShiftMonitoring(min_learning_samples=10, sample_length=sample_length, min_inference_samples=10, persistent=False, plot_folder=f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs", plot_on=True, return_input=True)
    shift.install()
    shift.add_parent(lba)

    for i in range(50):
        time.sleep(0.5)
        shift.execute()
        data = shift.buffer.data(persistent=False) # We extract the last two samples
        print(data)
        
        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data["values"])) == 10 
                assert len(list(data["values"])[0]) == 2
                assert len(list(data.values())) == 4 # Signal buffer returns two keys: values and timestamps and for each key one value is returned"""


def test_006():
    "Test Basic Functionality on UCR Data."
    
    sample_length = 2

    signal = DatasetBuffer(dataset_name="Car", sort_by_y=True)
    signal.install()
    
    lba = LinkBufferAction()
    lba.buffer = signal

    shift = ShiftMonitoring(min_learning_samples=10, sample_length=sample_length, features_from_parent=["values"], min_inference_samples=3, plot_folder=f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs", plot_on=True, persistent=False, return_input=True)
    shift.install()
    shift.add_parent(lba)

    for i in range(100):
        time.sleep(0.5)
        shift.execute()
        data = shift.buffer.data(persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data["values"])) == 3 
                assert len(list(data["values"])[0]) == 2
                assert len(list(data.values())) == 3 # values, feature-decision, feature-shift




def test_007():
    "Test Functionality on Blobs data without feature extraction to really identify shifts in data."
    

    signal = DatasetBuffer(dataset_name="Blobs", sort_by_y=True)
    signal.install()
    
    lba = LinkBufferAction()
    lba.buffer = signal


    shift = ShiftMonitoring(min_learning_samples=200, sample_length=2, min_inference_samples=1, persistent=False, features_from_parent=["values"], return_input=True, sensitivity=2) #1800
    shift.install()
    shift.add_parent(lba)

    fig, ax = plt.subplots()
    #plt.ion()
    for i in range(500):
        time.sleep(0.1)
        #chronos.execute()
        #pca.execute()
        shift.execute()
        data = shift.buffer.data(persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        print(data)
        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data["values"])[0]) == 2
                assert len(list(data.values())) == 3 # values, feature-decision, feature-shift
                
                if data["values-feature-shift"][0] == 0.0010442282266369285:
                    assert data["values-feature-decision"][0] == 1, f"At value 0.0010442282266369285 a shift should be detected but {data['values-feature-decision'][0]} was detected."
                if data["values-feature-shift"][0] == 1.2416197377085876e-05:
                    assert data["values-feature-decision"][0] == 0, f"At value 1.2416197377085876e-05 no shift should be detected but {data['values-feature-decision'][0]} was detected."
                if data["values-feature-shift"][0] == 0.001993711222241038:
                    assert data["values-feature-decision"][0] == 1, f"At value 0.001993711222241038 a shift should be detected but {data['values-feature-decision'][0]} was detected."
                

        if len(data.values()) > 0:
            if data["values-feature-decision"][0] == 0:
                color = 'g'
            elif data["values-feature-decision"][0] == None:
                color = 'b'
            else:
                color = 'r'
            #ax[2].scatter(data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][0], data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][1], color=color)
            #plt.pause(0.05)
            ax.scatter(data["values"][-1][0], data["values"][-1][1], color=color)
        if i % 10 == 0:
            pass
            fig.savefig(f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs/shiftmonitoring_test007_plot_iteration{i}.png")
        #fig.show()



def test_008():
    "Test Functionality on ECG5000 data with feature extraction."
    # ECG5000 Length for class 1: 400.000 Datapoints. Length for "one-sample" = 140 Points.
    # Car Length for class 1: 10.000 Datapoints. Length for "one-sample" = 577 Points.
    # ChlorineConcentration Length for class 1: 166500 Datapoints. Length for "one-sample" = 166 Points.
    

    signal = DatasetBuffer(dataset_name="ECG5000", sort_by_y=True)
    signal.install()

    signal_2 = DatasetBuffer(dataset_name="ECG5000", sort_by_y=True)
    signal_2.install()
    
    lba = LinkBufferAction()
    lba.buffer = signal

    lba_2 = LinkBufferAction()
    lba_2.buffer = signal_2

    chronos = ChronosExtractor(sample_length=140, persistent=False, normalize=True, features_from_parent=["values"]) 
    chronos.install()
    chronos.add_parent(lba)

    pca = PCADimReduction(dimensions=2, min_learning_samples=400, sample_length=384, min_inference_samples=1,normalize=True, features_from_parent=["values-feature-amazon-chronos-bolt-mini-0"], persistent=False) #384
    pca.install()
    pca.add_parent(chronos) # Rad data is passed to PCA directly to have a more direct connection between input data and PCA output.

    shift = ShiftMonitoring(min_learning_samples=2000, sample_length=2, min_inference_samples=1, persistent=False, features_from_parent=["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"], return_input=True, sensitivity=2) #1800
    shift.install()
    shift.add_parent(pca)

    fig, ax = plt.subplots(2,1)
    #plt.ion()
    for i in range(5000):
        time.sleep(0.1)
        chronos.execute()
        pca.execute()
        shift.execute()
        data = shift.buffer.data(persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        data_2 = lba_2.buffer.data(n=140, persistent=False)
        print(data)
        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data['values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift'])[0]) == 1
                assert len(list(data.values())) == 3 # Input data is returned in this test. 
                
                if data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift"][0] == 5.407847548518865e-05:
                    assert data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"][0] == 1, f"At value 5.407847548518865e-05 a shift should be detected but {data['values-feature-decision'][0]} was detected."
                if data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift"][0] == 3.308598942337312e-06:
                    assert data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-decision"][0] == 1, f"At value 3.308598942337312e-06 a shift should be detected but {data['values-feature-decision'][0]} was detected."


        if len(data.values()) > 0:
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
                ax[0].scatter(data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][0], data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][1], color=color)
                ax[0].set_title("Prediction")
                ax[1].scatter(data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][0], data["values-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][1], color=g_color)
                ax[1].set_title("Groundtruth")
            if i % 10 == 0:
                fig.savefig(f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs/shiftmonitoring_test007_plot_iteration{i}.png")


def test_009():
    "Test Functionality on ECG5000 data with ROCKET feature extraction."
    # ECG5000 Length for class 1: 400.000 Datapoints. Length for "one-sample" = 140 Points.
    # Car Length for class 1: 10.000 Datapoints. Length for "one-sample" = 577 Points.
    # ChlorineConcentration Length for class 1: 166500 Datapoints. Length for "one-sample" = 166 Points.
    
    

    signal = DatasetBuffer(dataset_name="ECG5000", sort_by_y=True)
    signal.install()

    signal_2 = DatasetBuffer(dataset_name="ECG5000", sort_by_y=True)
    signal_2.install()
    
    lba = LinkBufferAction()
    lba.buffer = signal

    lba_2 = LinkBufferAction()
    lba_2.buffer = signal_2

    #chronos = ChronosExtractor(sample_length=140, persistent=False, normalize=True, features_from_parent=["values"]) 
    rocket = ROCKETExtractor(sample_length=140, persistent=False, normalize=True, features_from_parent=["values"])
    rocket.install()
    rocket.add_parent(lba)

    pca = PCADimReduction(dimensions=2, min_learning_samples=600, sample_length=20000, min_inference_samples=1,normalize=True, features_from_parent=["values-feature-ROCKET-0"], persistent=False) #400
    pca.install()
    pca.add_parent(rocket) # Rad data is passed to PCA directly to have a more direct connection between input data and PCA output.

    shift = ShiftMonitoring(min_learning_samples=2000, sample_length=2, min_inference_samples=1, persistent=False, features_from_parent=["values-feature-ROCKET-0-feature-PCA"], return_input=True, sensitivity=2) #2000
    shift.install()
    shift.add_parent(pca)

    fig, ax = plt.subplots(2,1)
    #plt.ion()
    for i in range(5000):
        #time.sleep(0.1)
        rocket.execute()
        pca.execute()
        shift.execute()
        data = shift.buffer.data(persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        data_2 = lba_2.buffer.data(n=140, persistent=False)
        print(data)
        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data['values-feature-ROCKET-0-feature-PCA-feature-shift'])[0]) == 1
                assert len(list(data.values())) == 3 # Input data is returned in this test. 
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
                ax[0].scatter(data["values-feature-ROCKET-0-feature-PCA"][-1][0], data["values-feature-ROCKET-0-feature-PCA"][-1][1], color=color)
                ax[0].set_title("Prediction")
                ax[1].scatter(data["values-feature-ROCKET-0-feature-PCA"][-1][0], data["values-feature-ROCKET-0-feature-PCA"][-1][1], color=g_color)
                ax[1].set_title("Groundtruth")
            if i % 10 == 0:
                fig.savefig(f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs/shiftmonitoring_test007_plot_iteration{i}.png")



def test_010():
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
    lba.buffer = signal

    lba_2 = LinkBufferAction()
    lba_2.buffer = signal_2

    chronos = ChronosExtractor(sample_length=500, persistent=False, normalize=True, features_from_parent=["values_0"]) 
    #rocket = ROCKETExtractor(sample_length=500, persistent=False, normalize=True, features_from_parent=["values"])
    chronos.install()
    chronos.add_parent(lba)

    pca = PCADimReduction(dimensions=2, min_learning_samples=200, sample_length=500, min_inference_samples=1,normalize=True, features_from_parent=["values_0"], persistent=False) #400
    pca.install()
    pca.add_parent(lba) 
    shift = ShiftMonitoring(min_learning_samples=1200, sample_length=2, min_inference_samples=1, persistent=False, features_from_parent=["values_0-feature-PCA"], return_input=True, sensitivity=2) #2000
    shift.install()
    shift.add_parent(pca)

    fig, ax = plt.subplots(2,1)
    #plt.ion()
    for i in range(50000):
        #time.sleep(0.1)
        #chronos.execute()
        pca.execute()
        shift.execute()
        data = shift.buffer.data(persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        data_2 = lba_2.buffer.data(n=500, persistent=False)
        print(data)
        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data['values_0-feature-PCA-feature-shift'])[0]) == 1
                assert len(list(data.values())) == 3 # Input data is returned in this test. 
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
                ax[0].scatter(data["values_0-feature-PCA"][-1][0], data["values_0-feature-PCA"][-1][1], color=color)
                ax[0].set_title("Prediction")
                ax[1].scatter(data["values_0-feature-PCA"][-1][0], data["values_0-feature-PCA"][-1][1], color=g_color)
                ax[1].set_title("Groundtruth")
            if i % 10 == 0:
                fig.savefig(f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs/shiftmonitoring_test007_plot_iteration{i}.png")




def test_011():
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
    lba.buffer = signal

    lba_2 = LinkBufferAction()
    lba_2.buffer = signal_2

    chronos = ChronosExtractor(sample_length=100, persistent=False, normalize=True, features_from_parent=["values_0"]) 
    #rocket = ROCKETExtractor(sample_length=500, persistent=False, normalize=True, features_from_parent=["values"])
    chronos.install()
    chronos.add_parent(lba)

    pca = PCADimReduction(dimensions=2, min_learning_samples=400, sample_length=384, min_inference_samples=1,normalize=True, features_from_parent=["values_0-feature-amazon-chronos-bolt-mini-0"], persistent=False) #400
    pca.install()
    pca.add_parent(chronos) 
    shift = ShiftMonitoring(min_learning_samples=600, sample_length=2, min_inference_samples=1, persistent=False, features_from_parent=["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA"], return_input=True, sensitivity=2) #2000
    shift.install()
    shift.add_parent(pca)

    fig, ax = plt.subplots(2,1)
    #plt.ion()
    for i in range(50000):
        #time.sleep(0.1)
        chronos.execute()
        pca.execute()
        shift.execute()
        data = shift.buffer.data(persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        data_2 = lba_2.buffer.data(n=100, persistent=False)
        print(data)
        if len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data['values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA-feature-shift'])[0]) == 1
                assert len(list(data.values())) == 3 # Input data is returned in this test. 
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
                ax[0].scatter(data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][0], data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][1], color=color)
                ax[0].set_title("Prediction")
                ax[1].scatter(data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][0], data["values_0-feature-amazon-chronos-bolt-mini-0-feature-PCA"][-1][1], color=g_color)
                ax[1].set_title("Groundtruth")
            if i % 10 == 0:
                fig.savefig(f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs/shiftmonitoring_test007_plot_iteration{i}.png")


