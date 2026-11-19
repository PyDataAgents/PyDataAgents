from pydag.services.iolink.sensors.VVB301.abstract_blob_data_receiver import AbstractBlobDataReceiver, BlobType
from pydag.services.iolink.sensors.VVB301.definitions import HistData, MeasuringAxis, RawData


class AbstractRawDataReceiver(AbstractBlobDataReceiver):
    """
    blob_data_receiver
    ===========
    Houses the receivers used by clients to further processing history data and raw data.
    The data for the receivers comes from triggering a BLOB read flow from the sensor
    """

    """
        class AbstractRawDataReceiver
        ===========
        Class receives raw data from the device. Specify the axis from which this raw data comes from before passing this as an argument to the library.

        Data comes at the end of the BLOB transmission flow. It is presented to the user in 2 parts: header and actual data. Each represents a dictionary where keys are taken from :mod:`definitions.RawData`.
        The class documents to an extent the meaning and wether they are header or data related. Some information is common with the one retrieved through processs data so some keys are shared with :mod:`definitions.PD`
        Check the official documentation though as well for detailed meanings.

    """
    
    def __init__(self):
        super().__init__(BlobType.RawData)
        #raw data needs to specify the source from which raw data values come from, used when running the task
        self.specific_info[RawData.axis_src] = MeasuringAxis.XYZ_AXIS_EACH_4S

    def _on_blob_done(self, blob):
        super()._on_blob_done(blob)
        if self._type is BlobType.RawData and self._raw_header:
            self.on_client_raw_data_transfered(self._raw_header, self._raw_data)
    
    def set_measuring_axis(self, axis:MeasuringAxis):
        """
        set_measuring_axis Sets the measuring axis from which raw data will get retried

        Set before passing the receiver to the library.

        :param axis: axis and quantity of recording , see :class:`definitions.MeasuringAxis` for values and the IODD parameter "Raw data source SEL" for further details
        :type axis: :class:`definitions.MeasuringAxis`
        """
        self.specific_info[RawData.axis_src] = axis
    
    #this class doesn't handle information on this level
    def on_client_blob_segment(self, blod_segment_data):
        """
        on_client_blob_segment called when BLOB_Segment is sent by the device. Part of the BLOB tansmission protocol. Raw data does not interpret the data incrementally (as it comes) for now.

        Left for clients that need it to expand functionality

        :param blod_segment_data: binary data sent by the sensor
        :type blod_segment_data: bytearray
        :return: None
        """
        return None
    

    def on_client_raw_data_transfered(self, header_data, raw_data):
        """
        on_client_raw_data_transfered Called once the transmission of the raw data has finished and the data has been parsed. It is split in 2: a header part and a data part

        Keys are taken from :class:`definitions.RawData`. The header typically has most of the values there while the data has one or all 3 of [RawData.data_x_axis, RawData.data_y_axis, RawData.data_z_axis]
        depending on the selected measurement axis set, alongside with timestamp information (the :mod:`definitions.TIMESTAMP_KEY` key). Timestamps are in microseconds and aid in plotting the data points

        :param header_data: Dictionary of values whose keys are from :class:`definitions.RawData` and  :class:`definitions.PD`(since their meanings are similar like PD.v_rms_*, PD.a_peak* ...)
        :type header_data: dictionary
        :param raw_data: Raw data stored in numpy array who is indexed in a dictionrary by one or all of the following keys: [RawData.data_x_axis, RawData.data_y_axis, RawData.data_z_axis]
        alongside timestamps stored as an numpy array under the :mod:`definitions.TIMESTAMP_KEY` key
        :type raw_data: dictionary
        :raises NotImplementedError: Intended to be implemented by the client
        """
        raise NotImplementedError("Subclasses must implement this method")
    
# class extracts the process history data from the blob transfered data and forwards it to clients to use when ready
# unlike raw data this class can give incremental history data as the blob transfer advances
# clients should subclass and override the on_client_history_data_transfered method
"""
    class AbstractHistoryDataReceiver
    ===========
    Class receives history data from the device. It has the capabilities to deal with the data incrementally as it comes from the device, or once at the end of transmission

    Data comes at the end of the BLOB transmission flow. It is presented to the user in 2 parts: header and actual data. Each represents a dictionary where keys are taken from :class:`definitions.HistData`
    and partially from :class:`definitions.RawData` because of similarity.

"""
class AbstractHistoryDataReceiver(AbstractBlobDataReceiver):
    
    def __init__(self):
        super().__init__(BlobType.HistoryData)
        self.progress = 0.0
    
    def _on_blob_done(self, blob):
        super()._on_blob_done(blob)
        self.progress = 100.0
        # the base should have handled everything , this is just a formality
        if self.data_type() is BlobType.HistoryData and self._history_header:
            self.on_client_history_data_transfered(self._history_header, self._history_data)
    
    def _on_blob_segment(self, expected_blob_size:int, blog_segment_data:bytearray):
        """
        _on_blob_segment Exemplifies how to provide incremental updates as the reading of history is carried out in the background
        Useful when wanting to extend functionality

        :param expected_blob_size: total expected size in bytes of the blob data to be transfered
        :type expected_blob_size: integer
        :param blog_segment_data: chunk of blob data 
        :type blog_segment_data: bytearray
        """
        #update the progress indicator
        self.progress += (len(blog_segment_data) / expected_blob_size) * 100.00

        #take note of the number of elements before
        entries_before = 0
        if self._history_data:
            entries_before = len(self._history_data[HistData.uptime])
        super()._on_blob_segment(expected_blob_size,blog_segment_data)
        if self._history_data:
            added_elements = len(self._history_data[HistData.uptime]) - entries_before
            if added_elements > 0:
                increment_history_data = {key : value[-added_elements:] for key, value in self._history_data.items()}
                self.on_client_history_data_increment(self._history_header, increment_history_data)
        
        
    
    def on_client_history_data_transfered(self, header_data, history_data):
        """
        on_client_history_data_transfered Called once the whole read of process history data has been finished and the whole data parsed


        :param header_data: dictionary of keys and values representing the header of the history data. Keys are from :class:`definitions.HistData` and :class:`definitions.RawData`
        :type header_data: dictionary
        :param history_data: dictionary representing the actual processed data in the form of indexed keys and list of values. Values are from :class:`definitions.HistData` plus the :class:`definitions.TIMESTAMP_KEY`
        which gives holds timestamps in microseconds useful in ploting the data. The time is computed based on the `uptime` value (which is the time in seconds until the device got powered on) and the current timestamp.
        :type history_data: dictionary
        :raises NotImplementedError: Intended to be implemented by the client
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def on_client_history_data_increment(self, header_data, history_data):
        """
        on_client_history_data_increment Callback for the client when we have new parsed history data available while the whole read process is still ongoing

        Header data is the same as for :func:`on_client_history_data_transfered`. History data can contain 1 or more entries ,
        depending on how much data was sent via the BLOB transfer and the format of the history data.
        For a naive handling of the data check :class:'data_plotter.HistoryCacher`

        :param header_data: see :func:`on_client_history_data_transfered`
        :type header_data: dictionary
        :param history_data: see :func:`on_client_history_data_transfered`
        :type history_data: dictionary
        :raises NotImplementedError: Intended to be implemented by the client
        """
        raise NotImplementedError("Subclasses must implement this method")
    
class RawDataCacher(AbstractRawDataReceiver):
        
        def __init__(self):
            super().__init__()
            self._all_data = None
        
        def on_client_raw_data_transfered(self, header_data, raw_data):
            self._all_data = raw_data
            
        def get_data(self):
            return self._all_data