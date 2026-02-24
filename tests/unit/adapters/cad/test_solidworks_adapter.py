import pytest
import win32com.client
import pythoncom

from pydag.utils.FileUtils import FileUtils


def test_000():
    import sys, platform, win32com.client, pythoncom
    py_bits = platform.architecture()[0]
    print(f'Python bitness: {py_bits}')
    try:
        pythoncom.CoInitialize()
        sw = win32com.client.GetActiveObject('SldWorks.Application')
        print('SolidWorks is running')
        sw_bits = '64bit' if sw.Is64Bit() else '32bit'
        print(f'SolidWorks bitness: {sw_bits}')
        print('Bitness match!' if py_bits == sw_bits else ' Bitness mismatch!')
    except Exception as e:
        print('SolidWorks is NOT running:', e)

@pytest.mark.skip(reason="not correctly implemented yet") 
def test_010():

    # Required for some COM calls
    pythoncom.CoInitialize()

    # ---- USER SETTINGS ----
    PART_PATH = FileUtils.user_home() +  "\\Downloads\\models\\part1.SLDPRT"
    DIMENSION_NAME = "D1@Skizze1"   # <-- IMPORTANT
    NEW_VALUE_MM = 50               # value in millimeters
    # -----------------------

    # Convert mm → meters (SolidWorks API uses meters)
    new_value_m = NEW_VALUE_MM / 1000.0

    # Start SolidWorks
    swApp = win32com.client.Dispatch("SldWorks.Application")
    swApp.Visible = True

    # Open the part
    errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

    model = swApp.OpenDoc6(
        PART_PATH,
        1,      # swDocPART
        0,      # swOpenDocOptions_Silent
        "",
        errors,
        warnings
    )

    if not model:
        raise RuntimeError("Failed to open model")

    # Get the parameter (dimension)
    param = model.Parameter(DIMENSION_NAME)

    if not param:
        raise RuntimeError(f"Dimension '{DIMENSION_NAME}' not found")

    # Set the new value
    param.SystemValue = new_value_m

    # Force rebuild
    model.EditRebuild3()

    print(f"Dimension {DIMENSION_NAME} set to {NEW_VALUE_MM} mm")
    

@pytest.mark.skip(reason="not correctly implemented yet")    
def test_011():

    # Required for some COM calls
    pythoncom.CoInitialize()

    # ---- USER SETTINGS ----
    PART_PATH = FileUtils.user_home() +  "\\Downloads\\models\\part1.SLDPRT"
    DIMENSION_NAME = "D1@Skizze1"   # <-- IMPORTANT
    NEW_VALUE_MM = 65               # value in millimeters
    # -----------------------

    # Convert mm → meters (SolidWorks API uses meters)
    new_value_m = NEW_VALUE_MM / 1000.0

    # Start SolidWorks or get active application
    try:
        swApp = win32com.client.GetActiveObject("SldWorks.Application")
        print("Connected to existing SolidWorks session")
    except Exception:
        swApp = win32com.client.Dispatch("SldWorks.Application")
        print("opened new SolidWorks session")
    
    swApp.Visible = True

    # Open the part
    errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

    model = swApp.OpenDoc6(
        PART_PATH,
        1,      # swDocPART
        0,      # swOpenDocOptions_Silent
        "",
        errors,
        warnings
    )

    if not model:
        raise RuntimeError("Failed to open model")

    # Get the parameter (dimension)
    param = model.Parameter(DIMENSION_NAME)

    if not param:
        raise RuntimeError(f"Dimension '{DIMENSION_NAME}' not found")

    # Set the new value
    param.SystemValue = new_value_m

    # Force rebuild
    model.ForceRebuild3(False)

    print(f"Dimension {DIMENSION_NAME} set to {NEW_VALUE_MM} mm")
    
    success = model.Save3(1, errors, warnings)  # 1 = swSaveAsOptions_Silent
    if not success:
        print("Save failed")
    else:
        print("Model saved")
        
@pytest.mark.skip(reason="not correctly implemented yet")         
def test_020():
    pythoncom.CoInitialize()

    # Attach to running SolidWorks
    swApp = win32com.client.GetActiveObject("SldWorks.Application")
    model = swApp.ActiveDoc

    params = model.GetAllParameters()

    print(f"Found {len(params)} parameters:\n")

    for p in params:
        name = p.Name                # e.g. D1@Sketch1
        value_m = p.SystemValue      # meters
        value_mm = value_m * 1000.0

        print(f"{name} = {value_mm:.3f} mm")