import matplotlib.pyplot as plt
import time
import numpy as np
import pytest


from pydag.nodes.buffers.LinkBufferAction import LinkBufferAction
from pydag.buffers.signals.Sine import Sine
from pydag.buffers.SignalBuffer import SignalBuffer
from pydag.buffers.DatasetBuffer import DatasetBuffer
from pydag.nodes.featureextraction.ChronosExtractor import ChronosExtractor
from pydag.nodes.clustering.ShiftMonitoring import ShiftMonitoring
from pydag.nodes.dimreduction.PCADimReduction import PCADimReduction


def test_pca_returns_last_n_samples():

    n = 2

    signal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=signal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)
    lba.install()

    
    chronos = ChronosExtractor()
    chronos.install()
    chronos.add_parent(lba)

    pca = PCADimReduction(dimensions=2, min_learning_samples=10, sample_length=4, min_inference_samples=1, input_keys=["ChronosExtractor-feature-0"], persistent=False)
    pca.install()
    pca.add_parent(chronos)

    for i in range(20):
        time.sleep(0.1)
        chronos.execute()
        pca.execute()
        data = pca.get_buffer().data(n=n, persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        print(data)
        
        if hasattr(data, "values") and "values" in data:
            l_1 = len(next(iter(data.values())))
            assert l_1 > 0 and l_1 == n, f"Data length out of bounds: {l_1}"
            
    sine_buff.uninstall()



def test_shift_monitoring_with_pca_on_sine():
    "Test Basic Functionality on Sine Data as well as Plotting"
    n = 2

    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)
    lba.install()
    
    chronos = ChronosExtractor() # TODO: i dont think that this pipeline works with the ChronosExtractor default properties (sample_length = 0??)
    chronos.output_keys = ["CE-feature-1", "CE-feature-2"]
    chronos.install()
    chronos.add_parent(lba)

    pca = PCADimReduction(dimensions=2, min_learning_samples=10, sample_length=10, min_inference_samples=1, input_keys=["CE-feature-1"], output_keys=["PCA-feature-0"], persistent=False)
    pca.install()
    pca.add_parent(chronos)


    shift = ShiftMonitoring(min_learning_samples=10, sample_length=2, min_inference_samples=1, input_keys=["PCA-feature-0"], persistent=False)
    shift.install()
    shift.add_parent(pca)

    for i in range(10):
        time.sleep(0.5)
        chronos.execute()
        pca.execute()
        shift.execute()
        data = shift.get_buffer().data(persistent=True) # We extract the last two samples
        print(data)



def test_shift_monitoring_raw_sine_no_features():
    "Test Basic Functionality on Raw Sine Data (Without Feature Extraction and Dimensionality Reduction) as well as Plotting"
    n = 2

    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)
    lba.install()
    

    shift = ShiftMonitoring(min_learning_samples=10, sample_length=4, min_inference_samples=1, persistent=False)
    shift.install()
    shift.add_parent(lba)

    for i in range(10):
        time.sleep(0.5)
        shift.execute()
        data = shift.get_buffer().data(persistent=False) # We extract the last two samples
        print(data)
        if hasattr(data, "values") and len(data.values()) > 0:
            assert len(list(data.values())[0]) == 1 # Always one value is returned
            assert len(list(data.values())) == 6 # Signal buffer returns four keys: values-decision, values-shift, timestamps-decision and timestamps-shift and for each key one value is returned + timestamps and index



def test_shift_monitoring_raw_sine_more_inference_samples():
    "Test 002 but with more inference samples."
    n = 2

    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)
    lba.install()
    

    shift = ShiftMonitoring(min_learning_samples=10, sample_length=3, min_inference_samples=5, persistent=False)
    shift.install()
    shift.add_parent(lba)

    for i in range(10):
        time.sleep(0.5)
        shift.execute()
        data = shift.get_buffer().data(persistent=False)
        print(i)
        print(data)
        if hasattr(data, "values") and len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data.values())) == 6 # Signal buffer returns keys: values-decision, values-shift, timestamps-decision and timestamps-shift  and for each key one value is returned + timestamps and index
                assert all([isinstance(val, list) for val in data.values()]), "Values are not stored as lists."
                assert len(set([len(val) for val in data.values()])) == 1 # All lists must have the same length.

def test_shift_monitoring_raw_sine_return_input_values():
    "Test 002 but with more inference samples and input values returned"
    n = 2

    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)
    lba.install()
    

    shift = ShiftMonitoring(min_learning_samples=10, sample_length=3, min_inference_samples=5, persistent=False, return_input=True)
    shift.install()
    shift.add_parent(lba)

    for i in range(10):
        time.sleep(0.5)
        shift.execute()
        data = shift.get_buffer().data(persistent=False)
        print(i)
        print(data)
        if hasattr(data, "values") and len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data.values())) == 12 # Signal buffer returns: values-decision, values-shift, timestamps-decision, timestamps-shift values-0, values-1, values-2, timestamps-0, timestamps-1, timestamps-2 + timestamps and index
                assert all([isinstance(val, list) for val in data.values()]), "Values are not stored as lists."
                assert len(set([len(val) for val in data.values()])) == 1 # All lists must have the same length.


def test_shift_monitoring_return_input_two_channels():
    "Test Basic Functionality on Raw Sine Data (Without Feature Extraction and Dimensionality Reduction) as well as Plotting and return input data as well"
    sample_length = 2

    singal = Sine(f=1, a=1, p=0, n=0.1)
    sine_buff = SignalBuffer(signal=singal, capacity=1000)
    sine_buff.install()


    lba = LinkBufferAction()
    lba.set_buffer(sine_buff)
    lba.install()
    

    shift = ShiftMonitoring(min_learning_samples=10, sample_length=sample_length, min_inference_samples=1, persistent=False, return_input=True)
    shift.install()
    shift.add_parent(lba)

    for i in range(10):
        time.sleep(0.5)
        shift.execute()
        data = shift.get_buffer().data(persistent=False) # We extract the last two samples
        print(data)
        if hasattr(data, "values") and len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data.values())) == 10 # Signal buffer returns: values-decision, values-shift, timestamps-decision, timestamps-shift values-0, values-1, timestamps-0, timestamps-1 + timestamps and index
                assert all([isinstance(val, list) for val in data.values()]), "Values are not stored as lists."
                assert len(set([len(val) for val in data.values()])) == 1 # All lists must have the same length.




def test_shift_monitoring_on_ucr_car_dataset():
    "Test Basic Functionality on UCR Data."
    
    sample_length = 2

    signal = DatasetBuffer(dataset_name="Car", sort_by_y=True)
    signal.install()
    
    lba = LinkBufferAction()
    lba.set_buffer(signal)
    lba.install()
    
    shift = ShiftMonitoring(min_learning_samples=10, sample_length=sample_length, input_keys=["values"], min_inference_samples=3, persistent=False, return_input=True)
    shift.install()
    shift.add_parent(lba)

    for i in range(10):
        time.sleep(0.5)
        shift.execute()
        data = shift.get_buffer().data(persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        if hasattr(data, "values") and len(data.values()) > 0:
            if len(list(data.values())[0]) > 0:
                assert len(list(data.values())[0]) == 1 # Always one value is returned
                assert len(list(data.values())) == 6 # Signal buffer returns: values-decision, values-shift, values-0, values-1 + timestamps and index
                assert all([isinstance(val, list) for val in data.values()]), "Values are not stored as lists."
                assert len(set([len(val) for val in data.values()])) == 1 # All lists must have the same length.




def test_shift_monitoring_on_blobs_detects_shifts():
    "Test Functionality on Blobs data without feature extraction to really identify shifts in data."
    "Test that the returned data is correctly formatted as lists and has a consistent length."

    

    signal = DatasetBuffer(dataset_name="Blobs", sort_by_y=True)
    signal.install()
    
    lba = LinkBufferAction()
    lba.set_buffer(signal)
    lba.install()

    shift = ShiftMonitoring(min_learning_samples=200, sample_length=2, min_inference_samples=1, persistent=False, input_keys=["values"], return_input=True, sensitivity=2) #1800
    shift.install()
    shift.add_parent(lba)

    fig, ax = plt.subplots()
    #plt.ion()
    for i in range(20):
        time.sleep(0.1)
        #chronos.execute()
        #pca.execute()
        shift.execute()
        data = shift.get_buffer().data(persistent=False) # We extract the last two samples since PCA returns two dimensional data.
        print(data)
        if hasattr(data, 'values') and data is not None:
            if len(data.values()) > 0:
                if len(list(data.values())[0]) > 0:
                    assert len(list(data.values())[0]) == 1 # Always one value is returned
                    assert len(list(data.values())) == 6 # values-0, values-1, feature-decision, feature-shift + timestamps and index
                    assert all([isinstance(val, list) for val in data.values()]), "Values are not stored as lists."
                    assert len(set([len(val) for val in data.values()])) == 1 # All lists must have the same length.
                
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
                ax.scatter(data["values-0"], data["values-1"], color=color)
            if i % 10 == 0:
                pass
                #fig.savefig(f"C:/Users/tobia/Python Scripts/PyDataAgents-DataElements/resources/outputs/shiftmonitoring_test007_plot_iteration{i}.png")
            fig.show()

