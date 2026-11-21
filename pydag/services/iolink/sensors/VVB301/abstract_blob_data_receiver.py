from enum import IntEnum
import struct
import numpy as np
import time

from pydag.services.iolink.sensors.VVB301.definitions import PD, TIMESTAMP_KEY, HistData, MeasuringAxis, RawData
"""
    Class AbstractBlobDataReceiver
    =================
    Receivers deals with received BLOB data received as a result of triggering a raw data read or a history process data read.

    Its main role is to accumulate the data, interpret it accordingly, pre-process it and package it to be sent in the public part
    for the client to consume more easily. Raw data is scaled differently than history data. For convenience this class retains a
    copy of the final binary data for subclasses which needs it in the future.
    History data is interpreted in chunks as they are received while raw data is first accumulated, then at the end of the transmision
    interpreted accordingly to the set raw data trigger source set.
    Clients which need to pass in more information to this class to act upon should look at the specific_info attribute and set it in the
    subclasses and parse in the lower levels.

    :raises NotImplementedError: Those methods that are intended to be reimplemented by the client
"""
# An enum for the type of data we are querying
class BlobType(IntEnum):
    RawData = 0,
    HistoryData = 1

#this class merely interprets the blob data and passes it to the client who should implement the on_client_raw_data_transfered method for his needs
class AbstractBlobDataReceiver:
    __BLOB_HISTORY_HEADER_REQ_SIZE = 92
    __BLOB_HISTORY_ENTRY_REQ_SIZE = 88

    def __init__(self, data_type: BlobType):
        self._type = data_type
        self.blog_segment_counter = 0
        self._start_timestamp = None #used to deduce a timestamps for the values, approximately
        self._blob_accumulator = bytearray()
        self._history_header = {}
        self._history_data = {}
        self._history_data_keys_ordered = [] #ordered by the unpack order as blob data comes in
        self._raw_header = {}
        self._raw_data = {}
        self._blob_byte_data = bytearray()
        self.specific_info = {} #some extra input used in some flows, like measuring axis for raw data, intent is to be able to build upon it if needed
    
    # called when needed, resets the specific state related data such as to prepare for a next read
    def _reset(self):
        self.blog_segment_counter = 0
        self._start_timestamp = None #used to deduce a timestamps for the values, approximately
        self._blob_accumulator = bytearray()
        self._history_header.clear()
        self._history_header = {}
        self._history_data.clear()
        self._history_data = {}
        self._history_data_keys_ordered = [] #ordered by the unpack order as blob data comes in
        self._raw_header.clear()
        self._raw_header = {}
        self._raw_data.clear()
        self._raw_data = {}
        self._blob_byte_data.clear()

    def _on_blob_done(self, blob:bytearray):
        #for easy access to client subclassed receivers
        self._blob_byte_data = blob.copy()
        if self._type is BlobType.RawData:
            (self._raw_header, self._raw_data) = self._interpret_blob_raw(blob)
    
    def _on_blob_segment(self, expected_blob_size:int, blog_segment_data:bytearray):
        self.blog_segment_counter += 1
        if self._start_timestamp is None:
            self._start_timestamp =  time.time_ns() / 1000 #working in us for now
        if self._type is BlobType.HistoryData:
            self._blob_accumulator.extend(blog_segment_data)
            accumulated_size = len(self._blob_accumulator)
            if not self._history_header:
                if accumulated_size >= self.__BLOB_HISTORY_HEADER_REQ_SIZE:
                    self._interpret_blob_history_header(self._blob_accumulator)
                    self._blob_accumulator = self._blob_accumulator[self.__BLOB_HISTORY_HEADER_REQ_SIZE:]
            elif accumulated_size >= self.__BLOB_HISTORY_ENTRY_REQ_SIZE:
                self._interpret_blob_history_entry(self._blob_accumulator)
                trim_idx = (accumulated_size // self.__BLOB_HISTORY_ENTRY_REQ_SIZE) * self.__BLOB_HISTORY_ENTRY_REQ_SIZE
                self._blob_accumulator = self._blob_accumulator[trim_idx:]

    
    #this method assumes there is enough data in the bytearray
    def _interpret_blob_history_header(self, blob_data:bytearray):
        header_data = struct.unpack("IIBBBBBBBBBBBBHhHHHhffffffffffffffI", blob_data[:self.__BLOB_HISTORY_HEADER_REQ_SIZE])
        self._history_header = {
            RawData.h_length: header_data[0],
            RawData.dev_id: header_data[1],
            RawData.dev_sn: header_data[2:14],
            RawData.blob_id: header_data[14],
            RawData.reserved_1: header_data[15],
            RawData.vel_unit_id: header_data[16],
            RawData.acc_unit_id: header_data[17],
            RawData.temp_unit_id: header_data[18],
            RawData.reserved_2: header_data[19],
            HistData.sf_v_rms_x: header_data[20],
            HistData.sf_v_rms_y: header_data[21],
            HistData.sf_v_rms_z: header_data[22],
            HistData.sf_a_peak_x: header_data[23],
            HistData.sf_a_peak_y: header_data[24],
            HistData.sf_a_peak_z: header_data[25],
            HistData.sf_a_rms_x: header_data[26],
            HistData.sf_a_rms_y: header_data[27],
            HistData.sf_a_rms_z: header_data[28],
            HistData.sf_temp: header_data[29],
            HistData.sf_crest: header_data[30],
            HistData.sf_unbal: header_data[31],
            HistData.sf_bear: header_data[32],
            HistData.sf_rpm: header_data[33],
            HistData.content_len: header_data[34],
            HistData.vel_unit_str: "m/s" if header_data[16] == 1061 else "mm/s",
            HistData.acc_unit_str: "m/s²" if header_data[17] == 1076 else "mg0",
            HistData.temp_unit_str: "°C" if header_data[18] == 1001 else "°F" if header_data[18] == 1002 else "unknown"
        }
        self._history_data_keys_ordered = [
            HistData.uptime, HistData.v_rms_mean_x, HistData.v_rms_max_x, HistData.v_rms_min_x, HistData.v_rms_mean_y, HistData.v_rms_max_y, HistData.v_rms_min_y,
            HistData.v_rms_mean_z, HistData.v_rms_max_z, HistData.v_rms_min_z, HistData.a_peak_mean_x, HistData.a_peak_max_x, HistData.a_peak_min_x,
            HistData.a_peak_mean_y, HistData.a_peak_max_y, HistData.a_peak_min_y, HistData.a_peak_mean_z, HistData.a_peak_max_z, HistData.a_peak_min_z,
            HistData.a_Rms_mean_x, HistData.a_Rms_max_x, HistData.a_Rms_min_x, HistData.a_Rms_mean_y, HistData.a_Rms_max_y, HistData.a_Rms_min_y,
            HistData.a_Rms_mean_z, HistData.a_Rms_max_z, HistData.a_Rms_min_z, HistData.temp_mean, HistData.temp_max, HistData.temp_min, HistData.crest_mean,
            HistData.crest_max, HistData.crest_min, HistData.unbal_mean, HistData.unbal_max, HistData.unbal_min, HistData.bear_mean, HistData.bear_max, HistData.bear_min,
            HistData.rpm_mean, HistData.rpm_max, HistData.rpm_min ]
        # these scaling factors are applied to the history data, each one is applied to 3 data keys from the above list, excluding the , they are ordered to align with the data keys
        self._history_scaling_factors = [self._history_header[HistData.sf_v_rms_x], self._history_header[HistData.sf_v_rms_y], self._history_header[HistData.sf_v_rms_z], 
            self._history_header[HistData.sf_a_peak_x], self._history_header[HistData.sf_a_peak_y], self._history_header[HistData.sf_a_peak_z],
            self._history_header[HistData.sf_a_rms_x], self._history_header[HistData.sf_a_rms_y], self._history_header[HistData.sf_a_rms_z],
            self._history_header[HistData.sf_temp], self._history_header[HistData.sf_crest], self._history_header[HistData.sf_unbal], self._history_header[HistData.sf_bear], self._history_header[HistData.sf_rpm]]
        
        self._history_data = {hist_key : [] for hist_key in self._history_data_keys_ordered}
        #adding time stamp by hand as it is not easily available
        self._history_data[TIMESTAMP_KEY] = []
    
    def _interpret_blob_history_entry(self, blob_data:bytearray):
        process_values_per_entry = 14
        number_entries = len(blob_data) // self.__BLOB_HISTORY_ENTRY_REQ_SIZE
        format_string = "<I" + 'hhh' * process_values_per_entry
        start_index = 0
        for _ in range(number_entries):
            history_entry_data = struct.unpack(format_string, blob_data[start_index:start_index+self.__BLOB_HISTORY_ENTRY_REQ_SIZE])
            start_index += self.__BLOB_HISTORY_ENTRY_REQ_SIZE
            #first entry doesn't need scaling
            current_uptime_value = history_entry_data[0]
            self._history_data[self._history_data_keys_ordered[0]].append(current_uptime_value)
            
            for idx in range(1,len(history_entry_data)):
                #scale factor is always used for 3 terms according to how the data is being received
                scaled_value = float(history_entry_data[idx]) * self._history_scaling_factors[(idx-1)//3]
                self._history_data[self._history_data_keys_ordered[idx]].append(scaled_value)

            self._history_data[TIMESTAMP_KEY].append((time.time() - current_uptime_value)*1000000)


    def _interpret_blob_raw(self, blob:bytearray):
        raw_data_expected_header_len = 124
        if(len(blob) >= raw_data_expected_header_len):
            header_data = struct.unpack("<IIBBBBBBBBBBBBHhIffBBhfffffffffffffffffhHHHII", blob[:raw_data_expected_header_len]) 
            raw_data_type = header_data[20]
            header_raw_data = {}
            if raw_data_type in MeasuringAxis.__members__.values():
                #this is true for raw data
                header_raw_data = {
                    RawData.h_length: header_data[0],
                    RawData.dev_id: header_data[1],
                    RawData.dev_sn: header_data[2:14],
                    RawData.blob_id: header_data[14],
                    RawData.reserved_1: header_data[15],
                    RawData.content_len: header_data[16],
                    RawData.scale: header_data[17],
                    RawData.sample_freq: header_data[18],
                    RawData.trg_src: header_data[19],
                    RawData.axis_src: header_data[20],
                    RawData.reserved_2: header_data[21],
                    PD.v_rms_x: header_data[22],
                    PD.v_rms_y: header_data[23],
                    PD.v_rms_z: header_data[24],
                    PD.v_rms_mag: header_data[25],
                    PD.a_peak_x: header_data[26],
                    PD.a_peak_y: header_data[27],
                    PD.a_peak_z: header_data[28],
                    PD.a_peak_mag: header_data[29],
                    PD.a_rms_x: header_data[30],
                    PD.a_rms_y: header_data[31],
                    PD.a_rms_z: header_data[32],
                    PD.a_rms_mag: header_data[33],
                    PD.crest: header_data[34], #aCrest magnitude
                    RawData.temp_ext: header_data[35],
                    RawData.temp_int: header_data[36],
                    PD.unbalance: header_data[37],
                    RawData.bearing: header_data[38],
                    RawData.rpm_value: header_data[39],
                    RawData.vel_unit_id: header_data[40],
                    RawData.acc_unit_id: header_data[41],
                    RawData.temp_unit_id: header_data[42],
                    RawData.time_delta: header_data[43],
                    RawData.time_mot: header_data[44]
                }
            scale_factor = np.float64(header_data[17])
            raw_data_content = {}
            data_len = 0
            if raw_data_type == MeasuringAxis.XYZ_AXIS_EACH_4S:
                axis_data_length = header_raw_data[RawData.content_len] // 3
                start_index = raw_data_expected_header_len
                x_axis_data = self._unpack_and_scale_rawData(blob[start_index:start_index+axis_data_length],scale_factor)
                start_index += axis_data_length
                y_axis_data = self._unpack_and_scale_rawData(blob[start_index:start_index+axis_data_length],scale_factor)
                start_index += axis_data_length
                z_axis_data = self._unpack_and_scale_rawData(blob[start_index:start_index+axis_data_length],scale_factor)
                raw_data_content[RawData.data_x_axis] = x_axis_data.tolist()
                raw_data_content[RawData.data_y_axis] = y_axis_data.tolist()
                raw_data_content[RawData.data_z_axis] = z_axis_data.tolist()
                data_len = len(x_axis_data)
            else:
                axis_to_content_key = {MeasuringAxis.X_AXIS_4S: RawData.data_x_axis, MeasuringAxis.X_AXIS_12S: RawData.data_x_axis, MeasuringAxis.Y_AXIS_4S: RawData.data_y_axis,
                                     MeasuringAxis.Y_AXIS_12S: RawData.data_y_axis, MeasuringAxis.Z_AXIS_4S: RawData.data_z_axis, MeasuringAxis.Z_AXIS_12S: RawData.data_z_axis}
                axis_data = self._unpack_and_scale_rawData(blob[raw_data_expected_header_len:],scale_factor)
                raw_data_content[axis_to_content_key[raw_data_type]] = axis_data.tolist()
                data_len = len(axis_data)
            #generate the timestamps for the data by using the header and the data length
            delta_us_for_sample = 1000000.0 / header_raw_data[RawData.sample_freq]
            timestamps_us = [self._start_timestamp] * data_len
            for i in range(1,data_len):
                timestamps_us[i] = timestamps_us[i-1] + delta_us_for_sample
            raw_data_content[TIMESTAMP_KEY] = timestamps_us
            return (header_raw_data, raw_data_content)
        return (None,None)

    def _unpack_and_scale_rawData(self, byte_data:bytearray, scale_factor:np.float64):
        data_length = len(byte_data) // 2
        data_as_float = np.array(struct.unpack(f'<{data_length}h', byte_data), np.float64)
        data_as_float /= scale_factor
        return data_as_float
    

    def on_client_blob_segment(self, blod_segment_data:bytearray):
        raise NotImplementedError("Subclasses must implement this method")

    #for clients to see what kind of data they receive
    def data_type(self):
        return self._type