from enum import IntEnum

"""
definitions
===========
A place where all identifiers are grouped that is of importance to clients of the library.
Options for various methods, types and most importantly keys used to identify values from raw, history or process data

"""

#identifies the type of sensor/device
class VVBType(IntEnum):
    VVB301 = 301
    VVB302 = 302
    VVB305 = 305
    VVB306 = 306

#Option for how process data is queried
class ProcessDataQueryMethod(IntEnum):
    OneTime = 1, #get 1 entry of process data
    FiniteNumberOfTimes = 2, # queryies for specified number of times for process data then stops
    AtIntervalTimes = 3 # ever given ms it queries for an entry of process data indefinitely

#Units of measurement for velocity values to input as option where available
class VelocityUnits(IntEnum):
    mm_per_sec = 1 #millimeters per second
    in_per_sec = 2 #inches per second
    m_per_sec = 3 #meters per second

#Units of measurement for acceleration values to input as option where available
class AccelerationUnits(IntEnum):
    g_force = 4  #gravitational force equivalent
    mg_force = 5 #milli g-force
    m_per_sec_squared = 6 # m/s**2

class TemperatureUnits(IntEnum):
    celsius = 7
    fahrn = 8 #fahrenheit

TIMESTAMP_KEY = "Timestamp"
#process data keys for ease of query
class PD:
    #keys available for vvb301,vvb305 process data
    v_rms = "v-rms" #Fatigue (v-Rms) | Speed effective value
    v_axis = "v-axis" #Currently selected velocity axis
    a_peak = "a-peak" #Impact (a-Peak) | acceleration peak value
    a_rms = "a-rms" #Friction (a-Rms) | acceleration effective value
    a_axis = "a-axis" #Currently selected acceleration axis
    crest = "crest" #Acceleration crest factor
    temperature = "temperature" #Current temperature
    device_status = "device-status" #Current devce status, a copy of the parameter [Device Status] in the process data channel
    unbalance = "unbalance" #Current status  of the digital signal [Unbalance]
    v_ou1 = "v-ou1" #Current status of the digital signal [v-ou1]
    out1 = "out1" #Current status of the digital signal [OUT1]
    out2 = "out2"
    #keys particular to vvb302, vvb306 process data
    v_rms_x = "v-rms-x-axis" #Fatigue (v-Rms for x-Axis value)
    v_rms_y = "v-rms-y-axis" #Fatigue (v-Rms for y-Axis value)
    v_rms_z = "v-rms-z-axis" #Fatigue (v-Rms for z-Axis value)
    v_rms_mag = "v-rms-magnitude" #Fatigue (v-Rms for x-Axis value)
    a_peak_x = "a-peak-x-axis" #Impact (a-Peak) | acceleration peak value for the x-axis
    a_peak_y = "a-peak-y-axis" #Impact (a-Peak) | acceleration peak value for the y-axis
    a_peak_z = "a-peak-z-axis" #Impact (a-Peak) | acceleration peak value for the z-axis
    a_peak_mag = "a-peak-magnitude" #Impact (a-Peak magnitude value)
    a_rms_x = "a-rms-x-axis" #Friction (a-Rms) | acceleration effective value for the x axis
    a_rms_y = "a-rms-y-axis" #Friction (a-Rms) | acceleration effective value for the y axis
    a_rms_z = "a-rms-z-axis" #Friction (a-Rms) | acceleration effective value for the z axis
    a_rms_mag = "a-rms-magnitude" #Friction (a-Rms) | acceleration magnitude value
    #rest are common from the other vvbs' (device status , temperature etc). Consult the IODD document for what comes from the process data
    #next we have some constants relating to the process data's value for some of the values
    NO_DATA = 32764 #
    OL=32760 #overload
    UL = -32760 #underload

#Options to set the axis from which raw data is recorded. Its equivalent is the parameter Raw data source selection from the IODD document
class MeasuringAxis(IntEnum):
    XYZ_AXIS_EACH_4S = 0
    X_AXIS_4S = 1
    Y_AXIS_4S = 2
    Z_AXIS_4S = 3
    X_AXIS_12S = 4
    Y_AXIS_12S = 5
    Z_AXIS_12S = 6

#The type of response enum we can receive when querying for the Raw data avail. parameter from the IODD document
class RawDataAvailableResponse(IntEnum):
     NO_DATA_PRESENT = 0
     SYSCMD_DATA_PRESENT = 1
     EVENT_DATA_PRESENT = 2
     PDOUT_DATA_PRESENT = 3

#valid values for the BLOB_ID term from blob reading workflow
# indicates the channel from which the blob read accurs, its passed in the Blob_Start command
class BlobId(IntEnum):
     Idle = 0
     Read_RawData = -5002 # raw data record and read
     Read_RawData_Triggered = -5003 # read raw data triggered
     Read_ProcessData_History = -5004
     Read_Event_Log = -5001


#Details the possible values the header of BLOB_CH. While BLOB_CH has a variable structure it will always start with a 8-bit header, the values of which
# are available here. Part of the blob read flow.
class BlobCommands(IntEnum):
        Blob_Info_Read = 0x10
        Blob_Info_Write = 0x11
        Blob_Segment = 0x20
        Blob_Last = 0x30
        Blob_Crc = 0x40
        Blob_Abort = 0xF0
        Blob_Start = 0xF1
        Blob_Finish = 0xF2

class RawData:
     #key relating to the raw data header
     h_length = "header_length"
     dev_id = "iol_device_Id"
     dev_sn = "iol_serialNumber" #12 byte array
     blob_id = "iol_blob_Id"
     reserved_1 = "reserved_1"
     content_len = "rawData_length"  #size of raw data content in bytes
     scale = "rawData_scale" # raw data scaling factor to get 1[g] normed values (x[g0] = x / scale)
     sample_freq = "rawData_fs" #raw data scaling sampling frequency in [Hz]
     trg_src = "rawDataTrgSrc" # raw data trigger source
     axis_src = "rawDataSrc" #axis from which we have recorded. One of MeasuringAxis vaulues
     # certain keys seem similar with the ones from process data so we will chose to re-use those
     # following are the ones which are new
     reserved_2 = "reserved_2"
     temp_ext = "temp_Ext" #process value temp-ext
     temp_int = "temp_Int" #process value temp-int
     rpm_value = "rpmValue" #prcess value current revolution value !?
     bearing = "bearing"
     vel_unit_id = "velocity_UnitID" 
     acc_unit_id = "acceleration_UnitID"
     temp_unit_id = "temperature_UnitID"
     time_delta = "timeStamp_delta"
     time_mot = "mot_time" #machine operating time
     data_x_axis = "rawData_xAxis" # raw data values for the x axis
     data_y_axis = "rawData_yAxis" # raw data values for the y axis
     data_z_axis = "rawData_zAxis" # raw data values for the z axis

#defines particular keys relating to history header and history data (if applicable)
#some keys are shared with raw data as the blob header seems to contain similar terms
# "sf" stands for scaling factor as a compromise between specificity and name length
class HistData:
     uptime = "uptime" # time in seconds since the device got powered on
     sf_v_rms_x = "scaling_factor_vRms_xAxis"
     sf_v_rms_y = "scaling_factor_vRms_yAxis"
     sf_v_rms_z = "scaling_factor_vRms_zAxis"
     sf_a_peak_x = "scaling_factor_aPeak_xAxis"
     sf_a_peak_y = "scaling_factor_aPeak_yAxis"
     sf_a_peak_z = "scaling_factor_aPeak_zAxis"
     sf_a_rms_x = "scaling_factor_aRms_xAxis"
     sf_a_rms_y = "scaling_factor_aRms_yAxis"
     sf_a_rms_z = "scaling_factor_aRms_zAxis"
     sf_temp = "scaling_factor_temp"
     sf_unbal = "scaling_factor_unbalance"
     sf_bear = "scaling_factor_bearing"
     sf_rpm = "scaling_factor_rpm"
     sf_crest = "scaling_factor_crest"
     content_len = "historyData_length"
     vel_unit_str = "velocity_unit_string"
     acc_unit_str = "acceleration_unit_string"
     temp_unit_str ="temperature_unit_string"
     #process data part following below
     v_rms_mean_x = "vRms_xAxis_mean"
     v_rms_min_x = "vRms_xAxis_min"
     v_rms_max_x = "vRms_xAxis_max"
     v_rms_mean_y = "vRms_yAxis_mean"
     v_rms_min_y = "vRms_yAxis_min"
     v_rms_max_y = "vRms_yAxis_max"
     v_rms_mean_z = "vRms_zAxis_mean"
     v_rms_min_z = "vRms_zAxis_min"
     v_rms_max_z = "vRms_zAxis_max"
     a_peak_mean_x = "aPeak_xAxis_mean"
     a_peak_min_x = "aPeak_xAxis_min"
     a_peak_max_x = "aPeak_xAxis_max"
     a_peak_mean_y = "aPeak_yAxis_mean"
     a_peak_min_y = "aPeak_yAxis_min"
     a_peak_max_y = "aPeakyAxis_max"
     a_peak_mean_z = "aPeak_zAxis_mean"
     a_peak_min_z = "aPeak_zAxis_min"
     a_peak_max_z = "aPeak_zAxis_max"
     a_Rms_mean_x = "aRms_xAxis_mean"
     a_Rms_min_x = "aRms_xAxis_min"
     a_Rms_max_x = "aRms_xAxis_max"
     a_Rms_mean_y = "aRms_yAxis_mean"
     a_Rms_min_y = "aRms_yAxis_min"
     a_Rms_max_y = "aRms_yAxis_max"
     a_Rms_mean_z = "aRms_zAxis_mean"
     a_Rms_min_z = "aRms_zAxis_min"
     a_Rms_max_z = "aRms_zAxis_max"
     temp_mean = "temperature_mean"
     temp_max = "temperature_max"
     temp_min = "temperature_min"
     unbal_mean = "unbalanace_mean"
     unbal_max = "unbalance_max"
     unbal_min = "unbalance_min"
     bear_mean = "bearing_mean"
     bear_max = "bearing_max"
     bear_min = "bearing_min"
     crest_mean = "crest_mean"
     crest_max = "crest_max"
     crest_min = "crest_min"
     rpm_mean = "rpm_mean"
     rpm_max = "rpm_max"
     rpm_min = "rpm_min"