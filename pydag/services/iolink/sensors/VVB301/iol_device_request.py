from copy import deepcopy
from string import Template
import struct

from pydag.services.iolink.sensors.VVB301.definitions import MeasuringAxis, VVBType
from pydag.services.iolink.sensors.VVB301.request_templates import _generic_device_template, _generic_request_template


class IolDeviceRequest:
    """
        class IolDeviceRequest
        ===========
        Class builds device oriented requests given input data. Its meant to be lightweight layer between the details relating to each request and application logic.
        Private methods usually offer the general functionality, where possible, while public ones are meant for client consumption. The various templates it uses are in the
        private part of the library, as clients as needn't be concerned with them. If you need to extend functionality you can look them up in :mod:`private.request_templates`
        The `type` parameter in the constructor doesn't apply to all requests. The port is required to identify the device in the IO Link Master which to query as almost all
        such requests target a device connected to the IO Link master.
        Further reading about how each request look can be found in Chaper 9 - ifm IoT Core -> Programmers notes from the Operating instructions manual of the IO Link master

    """
    
    def __init__(self, sensor_type:VVBType, iol_master_port:int ) -> None:
        self._sensor_type = sensor_type
        self._port = iol_master_port
        self._generic_request = deepcopy(_generic_request_template)
        self._device_request = deepcopy(_generic_device_template)
        temp_obj = Template(self._device_request["adr"])
        self._device_request["adr"] = temp_obj.substitute(port_number=self._port)
        self._device_parameter_data = {"index":"$index_number", "subindex":"0"}
    
    def _bound_cid_to_request(self, request, cid = None):
        cid_value = -1
        if cid is not None:
            cid_value = cid
        request["cid"] = cid_value
    
    def _get_device_parameter_value(self, index:int, subindex = 0, cid = None):
        """
        _get_device_parameter_value Generic method for getting a request for reading the value of a parameter from the IODD document.

        The data on an IO-Link device can be uniquely addressed with index and sub-index. The values for index and sub-index as well as the structure of the data 
        record can be found in the description of the IO-Link Device.

        :param index: index of the parameter data value
        :type index: integer
        :param subindex: subindex of the parameter data value, defaults to 0
        :type subindex: integer, optional
        :param cid: Correlation ID for the assignment of request and response; ID freely assignable by the user, defaults to None
        :type cid: integer, optional
        :return: request used to retrieve the parameter from the device
        :rtype: dictionary
        """
        request = deepcopy(self._device_request)
        self._bound_cid_to_request(request,cid)
        request_data = deepcopy(self._device_parameter_data)
        request_data["index"] = index
        request_data["subindex"] = subindex
        request["adr"] += "iolreadacyclic"
        request["data"] = request_data
        return request
    
    def _set_device_parameter_value(self, value, index:int, subindex = 0, cid = None):
        """
        _set_device_parameter_value Generic method for building a request to write to a specifc value to a parameter of the sensor

        The data on an IO-Link device can be uniquely addressed with index and sub-index. The values for index and sub-index as well as the structure of the data 
        record can be found in the description of the IO-Link Device.
        Ensure that the given index / sub-index combination leads to a parameter that is writeable, some can be read-only.

        :param value: the value needed to be written. For now simple integers or byte-arrays are supported only.
        :type value: integer or bytearray
        :param index: index of the writable parameter data value
        :type index: integer
        :param subindex: subindex of the writable parameter data value, defaults to 0
        :type subindex: integer, optional
        :param cid:  Correlation ID for the assignment of request and response; ID freely assignable by the user,, defaults to None
        :type cid: integer, optional
        :return: request which when sent writes the given value to the parameter identified by the index/sub-index combination
        :rtype: dictionary
        """
        request = deepcopy(self._device_request)
        self._bound_cid_to_request(request,cid)
        request_data = deepcopy(self._device_parameter_data)
        request_data["index"] = index
        request_data["subindex"] = subindex
        value_as_hex_string=""
        if isinstance(value,bytearray):
            value_as_hex_string = ''.join(format(b,"02x" ) for b in value)
        elif isinstance(value, int):
            value_as_hex_string = format(value,"02x")
        #value here needs to be given in hexadecimal format according to the IOL master programming notes
        request_data["value"] = value_as_hex_string
        request["adr"] += "iolwriteacyclic"
        request["data"] = request_data
        return request

    def sensor_type(self):
        """
        sensor_type Convenience getter for the sensor type


        :return: type of VVV3 sensor , see :class:`definitions.VVB3Type`
        :rtype: :class:`definitions.VVB3Type`
        """
        return self._sensor_type
    
    def get_device_id(self,cid = None):
        """
        get_device_id Assembles a request used to retrieve the device ID.

        :param cid: Correlation ID for the assignment of request and response, ID freely assignable by the user, defaults to None
        :type cid: integer, optional
        :return: request for IO Link Master to get the device ID
        :rtype: dictionary
        """
        request = deepcopy(self._device_request)
        self._bound_cid_to_request(request, cid)
        request["adr"] += "deviceid/getdata"
        return request
    
    def get_vendor_id(self,cid = None):
        """
        get_vendor_id Assembles a request used to retrieve the vendor ID for the device



        :param cid: Correlation ID for the assignment of request and response, ID freely assignable by the user, defaults to None
        :type cid: integer, optional
        :return: request for IO Link Master to get the vendor ID
        :rtype: dictionary
        """
        request = deepcopy(self._device_request)
        self._bound_cid_to_request(request, cid)
        request["adr"] += "vendorid/getdata"
        return request
    
    def get_device_status(self, cid = None):
        """
        get_device_status Assembles a request which read the device status parameter from the IODD document

        :param cid: Correlation ID for the assignment of request and response, ID freely assignable by the user, defaults to None
        :type cid: integer, optional
        :return: request used to read the device status of the device
        :rtype: dictionary
        """
        request = self._get_device_parameter_value(36, 0, cid)
        return request
    
    def get_device_tree(self, cid = None):
        """
        get_device_tree Assembles a request which gives the complete device tree of the device description as a json

        This a IO Link master feature, not a device specific feature

        :param cid: Correlation ID for the assignment of request and response, ID freely assignable by the user, defaults to None
        :type cid: integer, optional
        :return: request
        :rtype: dictionary
        """
        request = deepcopy(self._generic_request)
        self._bound_cid_to_request(request, cid)
        request["adr"] = "gettree"
        return request
    
    def get_process_data(self,cid = None):
        """
        get_process_data Assembles a request used to retrieve process data from the IO Link device.

        :param cid: Correlation ID for the assignment of request and response, ID freely assignable by the user, defaults to None
        :type cid: integer, optional
        :return: request
        :rtype: dictionary
        """
        request = deepcopy(self._device_request)
        self._bound_cid_to_request(request, cid)
        request["adr"] += "pdin/getdata"
        return request
    
    def set_process_data_out_raw_recording(self, enable_trigger_raw_data:bool, cid=None):
        """
        set_process_data_out_raw_recording Assembles a request that activates/deactivates the raw data trigger using the PDout value on pin 4 of the IO Link port

        :param enable_trigger_raw_data: True to enable, false to disable
        :type enable_trigger_raw_data: bool
        :param cid: Correlation ID for the assignment of request and response, ID freely assignable by the user, defaults to None
        :type cid: integer, optional
        :return: request
        :rtype: dictionary
        """
        request = deepcopy(self._device_request)
        self._bound_cid_to_request(request, cid)
        request["adr"] += "pdout/setdata"
        #the field contains both rpm value and this value, so both need to be supplied
        raw_data_enable = enable_trigger_raw_data << 4
        #first 0 is the rpm value, second is the high byte which from OOD contains nothing of value
        #while only the last one is the information we want to set
        byte_data = struct.pack(">hBB", 0, 0, raw_data_enable)
        #now this data needs to be converted to a hex string
        value_as_hex_string = ''.join(format(b,"02x" ) for b in byte_data)
        request["data"] = { "newvalue" : value_as_hex_string }
        return request
    
    def set_measuring_axis(self, option: MeasuringAxis, cid = None):
        """
        set_measuring_axis Assembles a request which writes the axis source argument. This value is used during a raw data read

        :param option: Enum which idenfies the axis/axes and duration
        :type option: :class:`definitions.MeasuringAxis`
        :param cid: Correlation ID for the assignment of request and response, ID freely assignable by the user, defaults to None
        :type cid: integer, optional
        :return: request
        :rtype: dictionary
        """
        request = self._set_device_parameter_value(option, 8016, 0, cid)
        return request
    
    def get_raw_data_available(self, cid = None):
        """
        get_raw_data_available Assembles a request which reads the `raw data avail.` parameter from the IODD document


        :param cid: Correlation ID for the assignment of request and response, ID freely assignable by the user, defaults to None
        :type cid: integer, optional
        :return: request
        :rtype: dictionary
        """
        request = self._get_device_parameter_value(8020,0,cid)
        return request
    
    def get_raw_data_read(self, cid = None):
        """
        get_raw_data_read Assembles a request used to read raw data. Generically its a BLOB_CH read according to the IO Link profile for blob data

        Used in the BLOB data transfer flow

        :param cid: Correlation ID for the assignment of request and response, ID freely assignable by the user, defaults to None
        :type cid: integer, optional
        :return: request
        :rtype: dictionary
        """
        request = self._get_device_parameter_value(50, 0, cid)
        return request
    
    def system_command_start_raw_data(self, cid = None):
        """
        system_command_start_raw_data Assembles a request representing a system command to instruct the device to start raw data recording

        :param cid: Correlation ID for the assignment of request and response, ID freely assignable by the user, defaults to None
        :type cid: integer, optional
        :return: request
        :rtype: dictionary
        """
        request = self._set_device_parameter_value(220, 2, 0, cid)
        return request
