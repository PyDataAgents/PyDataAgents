import ipaddress
import string

from pydag.services.iolink.sensors.VVB301.definitions import  VVBType


class DeviceInfo:
    """
    class DeviceInfo
    ===========
    A simple POD (Plain Old Data) for some of the required information needed to be passed to functions acrosss the library.
    Part of the information may present interest to the client as well.
    Typically available after a device scan on a IO-Link Master IP. Not necessarily meant to be constructed by the client.

    Attributes:
    -----------
    type: VVBType, one of [VVB301 VVB302 VVB305 VVB306] see :mod:`definitions`:
    ip: string that stores the IP address of the IO Link master to which the sensors are connected
    port: int that signifies the port number [X] on the IO Link master to which this sensor is connected
    dev_id: integer, the sensor's device id available from the IODD document of the device, populated after querying for a device
    vendor_id: integer ,id representing the vendor of this sensor, taken from the device.
    dev_status: integer, a number between 0-4 with specific interpretation according to the IODD document. For a string representation call :func:`device_status` on this object
    """
    def __init__(self, sensor_type: VVBType, master_ip:string, master_port:int, device_id: int, vendor_id:int, device_status:int):
        self.type = sensor_type
        self.ip = master_ip
        self.port = master_port
        self.dev_id = device_id
        self.vendor_id = vendor_id
        self.dev_status = device_status
    

    def device_status(self) -> str:
        """
        device_status Returns the device status code interpreted as a string

        This is a state retained on the client when the device info was created, typically upon discovery

        :return: The device status as a string
        :rtype: string
        """ 
        if self.dev_status == 0:
            return "Device OK"
        elif self.dev_status == 1:
            return "Maintenance required"
        elif self.dev_status == 2:
            return "Out of specification"
        elif self.dev_status == 3:
            return "Functional check"
        else:
            return "Failure"
    
    def valid(self) -> bool:
        """
        valid Checks if the information is valid

        Note: vendor id and device id are checked before creation by the library. For the purpose of mocking the class this extra test is omitted

        :return: True if the information is valid, False otherwise
        :rtype: bool
        """        
        isOk = False
        try:
            #omitting vendor and device validation here cause these object will be constructed
            isOk = self.dev_status == 0 and ipaddress.ip_address(self.ip) and self.port > 0 and self.port < 9
        except ValueError:
            isOk = False
        return isOk
