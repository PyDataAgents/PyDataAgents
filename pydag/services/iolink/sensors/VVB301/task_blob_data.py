import struct
import numpy as np
import functools

from pydag.services.iolink.sensors.VVB301.abstract_blob_data_receiver import AbstractBlobDataReceiver, BlobType
from pydag.services.iolink.sensors.VVB301.base_command import BaseCommand, Client
from pydag.services.iolink.sensors.VVB301.definitions import BlobCommands, BlobId, RawData, RawDataAvailableResponse
from pydag.services.iolink.sensors.VVB301.iol_device_request import IolDeviceRequest
from pydag.services.iolink.sensors.VVB301.repetitive_command import RepetitiveCommand

_READ_BLOB_DATA_CID = 50
_RAW_DATA_AVAILABLE_CID = 40
_RAW_DATA_RECORD_CID = 30

_SET_MEASURE_AXIS_CID = 20

# This class computes the CRC according to the crc32_octetwise solution presented int he IOL profile BLOB document
class CRCMaker:
    def __init__(self):
        self._lookup = [ 0x00000000, 0x9695C4CA, 0xFB4839C9, 0x6DDDFD03, 0x20F3C3CF, 0xB6660705, 0xDBBBFA06, 0x4D2E3ECC, 0x41E7879E, 0xD7724354, 0xBAAFBE57, 0x2C3A7A9D, 0x61144451, 0xF781809B, 0x9A5C7D98, 0x0CC9B952, 0x83CF0F3C, 0x155ACBF6, 0x788736F5, 0xEE12F23F, 0xA33CCCF3, 0x35A90839, 0x5874F53A, 0xCEE131F0, 0xC22888A2, 0x54BD4C68, 0x3960B16B, 0xAFF575A1, 0xE2DB4B6D, 0x744E8FA7, 0x199372A4, 0x8F06B66E, 0xD1FDAE25, 0x47686AEF, 0x2AB597EC, 0xBC205326, 0xF10E6DEA, 0x679BA920, 0x0A465423, 0x9CD390E9, 0x901A29BB, 0x068FED71, 0x6B521072, 0xFDC7D4B8, 0xB0E9EA74, 0x267C2EBE, 0x4BA1D3BD, 0xDD341777, 0x5232A119, 0xC4A765D3, 0xA97A98D0, 0x3FEF5C1A, 0x72C162D6, 0xE454A61C, 0x89895B1F, 0x1F1C9FD5, 0x13D52687, 0x8540E24D, 0xE89D1F4E, 0x7E08DB84, 0x3326E548, 0xA5B32182, 0xC86EDC81, 0x5EFB184B, 0x7598EC17, 0xE30D28DD, 0x8ED0D5DE, 0x18451114, 0x556B2FD8, 0xC3FEEB12, 0xAE231611, 0x38B6D2DB, 0x347F6B89, 0xA2EAAF43, 0xCF375240, 0x59A2968A, 0x148CA846, 0x82196C8C, 0xEFC4918F, 0x79515545, 0xF657E32B, 0x60C227E1, 0x0D1FDAE2, 0x9B8A1E28, 0xD6A420E4, 0x4031E42E, 0x2DEC192D, 0xBB79DDE7, 0xB7B064B5, 0x2125A07F, 0x4CF85D7C, 0xDA6D99B6, 0x9743A77A, 0x01D663B0, 0x6C0B9EB3, 0xFA9E5A79, 0xA4654232, 0x32F086F8, 0x5F2D7BFB, 0xC9B8BF31, 0x849681FD, 0x12034537, 0x7FDEB834, 0xE94B7CFE, 0xE582C5AC, 0x73170166, 0x1ECAFC65, 0x885F38AF, 0xC5710663, 0x53E4C2A9, 0x3E393FAA, 0xA8ACFB60, 0x27AA4D0E, 0xB13F89C4, 0xDCE274C7, 0x4A77B00D, 0x07598EC1, 0x91CC4A0B, 0xFC11B708, 0x6A8473C2, 0x664DCA90, 0xF0D80E5A, 0x9D05F359, 0x0B903793, 0x46BE095F, 0xD02BCD95, 0xBDF63096, 0x2B63F45C, 0xEB31D82E, 0x7DA41CE4, 0x1079E1E7, 0x86EC252D, 0xCBC21BE1, 0x5D57DF2B, 0x308A2228, 0xA61FE6E2, 0xAAD65FB0, 0x3C439B7A, 0x519E6679, 0xC70BA2B3, 0x8A259C7F, 0x1CB058B5, 0x716DA5B6, 0xE7F8617C, 0x68FED712, 0xFE6B13D8, 0x93B6EEDB, 0x05232A11, 0x480D14DD, 0xDE98D017, 0xB3452D14, 0x25D0E9DE, 0x2919508C, 0xBF8C9446, 0xD2516945, 0x44C4AD8F, 0x09EA9343, 0x9F7F5789, 0xF2A2AA8A, 0x64376E40, 0x3ACC760B, 0xAC59B2C1, 0xC1844FC2, 0x57118B08, 0x1A3FB5C4, 0x8CAA710E, 0xE1778C0D, 0x77E248C7, 0x7B2BF195, 0xEDBE355F, 0x8063C85C, 0x16F60C96, 0x5BD8325A, 0xCD4DF690, 0xA0900B93, 0x3605CF59, 0xB9037937, 0x2F96BDFD, 0x424B40FE, 0xD4DE8434, 0x99F0BAF8, 0x0F657E32, 0x62B88331, 0xF42D47FB, 0xF8E4FEA9, 0x6E713A63, 0x03ACC760, 0x953903AA, 0xD8173D66, 0x4E82F9AC, 0x235F04AF, 0xB5CAC065, 0x9EA93439, 0x083CF0F3, 0x65E10DF0, 0xF374C93A, 0xBE5AF7F6, 0x28CF333C, 0x4512CE3F, 0xD3870AF5, 0xDF4EB3A7, 0x49DB776D, 0x24068A6E, 0xB2934EA4, 0xFFBD7068, 0x6928B4A2, 0x04F549A1, 0x92608D6B, 0x1D663B05, 0x8BF3FFCF, 0xE62E02CC, 0x70BBC606, 0x3D95F8CA, 0xAB003C00, 0xC6DDC103, 0x504805C9, 0x5C81BC9B, 0xCA147851, 0xA7C98552, 0x315C4198, 0x7C727F54, 0xEAE7BB9E, 0x873A469D, 0x11AF8257, 0x4F549A1C, 0xD9C15ED6, 0xB41CA3D5, 0x2289671F, 0x6FA759D3, 0xF9329D19, 0x94EF601A, 0x027AA4D0, 0x0EB31D82, 0x9826D948, 0xF5FB244B, 0x636EE081, 0x2E40DE4D, 0xB8D51A87, 0xD508E784, 0x439D234E, 0xCC9B9520, 0x5A0E51EA, 0x37D3ACE9, 0xA1466823, 0xEC6856EF, 0x7AFD9225, 0x17206F26, 0x81B5ABEC, 0x8D7C12BE, 0x1BE9D674, 0x76342B77, 0xE0A1EFBD, 0xAD8FD171, 0x3B1A15BB, 0x56C7E8B8, 0xC0522C72]
        self._current_crc = 0x00000001
    
    def update_crc(self, byte_array):
        length = len(byte_array)
        crc = ~self._current_crc & 0xFFFFFFFF
        for i in range(length):
            crc = (crc >> 8) ^ self._lookup[(crc & 0xFF) ^ byte_array[i]]
        self._current_crc = ~crc & 0xFFFFFFFF
        return self._current_crc
    
    def get_crc(self):
        return self._current_crc

#class handles blob data transfer protocol
class BlobDataFlowClient(Client):
    def __init__(self, cmd_raw_data_available:RepetitiveCommand, cmd_read_raw_data:RepetitiveCommand, blob_receiver: AbstractBlobDataReceiver ):
        self._data_avail_cmd = cmd_raw_data_available
        self._read_raw_data = cmd_read_raw_data
        self._blob_size = 0
        self._raw_data_as_bytes = bytearray()
        self._crc_maker = CRCMaker()
        self._blob_receiver = blob_receiver
    
    def process_response(self, iol_master_response):
        response_cid = iol_master_response["cid"]
        if response_cid is _RAW_DATA_AVAILABLE_CID:
            self.handle_raw_data_available(iol_master_response)
        elif response_cid is _READ_BLOB_DATA_CID:
            self.handle_read_blob_data(iol_master_response)
    
    def handle_raw_data_available(self, iol_master_response):
        response_value = iol_master_response["data"]["value"]
        if int(response_value,16) != RawDataAvailableResponse.NO_DATA_PRESENT:
            #somewhere we have a raw data available, safe to stop now
            self._data_avail_cmd.abort_execution()
    
    def handle_read_blob_data(self, iol_master_response):
        if self.valid(iol_master_response):
            byte_data = bytes.fromhex(iol_master_response["data"]["value"])
            if byte_data[0] == BlobCommands.Blob_Info_Read and self._blob_size == 0:
                self._blob_size = int.from_bytes(byte_data[1:], byteorder="big", signed=False)
            elif self._blob_size > 0:
                blob_cmd = byte_data[0] & 0xF0
                if blob_cmd == BlobCommands.Blob_Segment or blob_cmd == BlobCommands.Blob_Last:
                    blob_useful_data = byte_data[1:]
                    self._raw_data_as_bytes.extend(blob_useful_data)
                    self._crc_maker.update_crc(blob_useful_data)
                    self._blob_receiver._on_blob_segment(self._blob_size, blob_useful_data)
                elif blob_cmd == BlobCommands.Blob_Crc:
                    blob_data = bytearray(byte_data[1:])
                    received_crc = int.from_bytes(blob_data, byteorder="big", signed=False)
                    if received_crc != self._crc_maker.get_crc():
                        raise ValueError("Received CRC differs from computed one.")
                    if self._blob_size != len(self._raw_data_as_bytes):
                        raise ValueError("Length of raw data is different from expected size.")
                    # this command also aborts the repetitive command
                    self._read_raw_data.abort_execution()
                    self._blob_receiver._on_blob_done(self._raw_data_as_bytes)
                else:
                    print("Received " + str(blob_cmd) + " command. No handle for it. Aborting execution . . .")
                    raise ValueError("Abort")


class QueryBlobDataTask:
    def __init__(self, request_maker: IolDeviceRequest, iol_master_url, blob_receiver: AbstractBlobDataReceiver = None):
        self._request_builder = request_maker
        self._master_url = iol_master_url
        read_blob_request = self._request_builder.get_raw_data_read(_READ_BLOB_DATA_CID)
        #simulate an infinite loop read, the 100000
        self._blob_data_read = RepetitiveCommand(self._master_url, read_blob_request, 100000)
        
        raw_data_available_request = self._request_builder._get_device_parameter_value(8020,0,_RAW_DATA_AVAILABLE_CID)
        self._wait_on_raw_data_available = RepetitiveCommand(self._master_url, raw_data_available_request, 0, 500)

        sys_cmd_start_recording_req = self._request_builder.system_command_start_raw_data(_RAW_DATA_RECORD_CID)
        self._start_recording = BaseCommand(self._master_url,"", sys_cmd_start_recording_req)
        self._blob_receiver = blob_receiver

        handle_read_raw_flow = BlobDataFlowClient(self._wait_on_raw_data_available, self._blob_data_read, self._blob_receiver)
        #need to attach the client who will handle the read flow of the blob while it finishes
        self._wait_on_raw_data_available.attach_client(handle_read_raw_flow)
        self._blob_data_read.attach_client(handle_read_raw_flow)
    
    def run(self):
        self._blob_receiver._reset()
        if self._blob_receiver.data_type() is BlobType.RawData and self._blob_receiver.specific_info:
            measure_axis = self._blob_receiver.specific_info[RawData.axis_src]
            set_measure_axis_request = self._request_builder.set_measuring_axis(measure_axis, _SET_MEASURE_AXIS_CID)
            self._execute_command(set_measure_axis_request)
            # send the start recording system command
            response = self._start_recording.execute()
            response_code = int(response["code"])
            if response_code != 200:
                error_number = int(response["error"],16)
                if response_code != 531 and error_number != 0x8020:
                    #this is a service temporarily unavailable because of something else, hopefully not a deal breaker
                    raise ValueError("Could not properly start the recording, return code:"+str(response_code))
            #wait until the raw data is available !?
            self._wait_on_raw_data_available.execute()
        #now we can actually start the reading flow
        if not self._is_blob_idle():
            self._execute_blob_abort()
        
        channelToStart = BlobId.Read_RawData if self._blob_receiver.data_type() is BlobType.RawData else BlobId.Read_ProcessData_History
        self._execute_blob_start(channelToStart)
        #this command has a client attached to it that handles the rest of the flow
        self._blob_data_read.execute()
        self._execute_blob_finish()
    
    def _is_blob_idle(self):
        check_blob_id_request = self._request_builder._get_device_parameter_value(49,0,_READ_BLOB_DATA_CID)
        cmd = BaseCommand(self._master_url, "", check_blob_id_request)
        response = cmd.execute()
        response_code = int(response["code"])
        if response_code != 200:
            raise ValueError("Failed to abort any previous read. Aborting . . .")
        response_data = int(response["data"]["value"],16)
        return response_data == 0

    def _execute_blob_abort(self):
        abort_request = self._request_builder._set_device_parameter_value(BlobCommands.Blob_Abort, 50, 0, _READ_BLOB_DATA_CID)
        self._execute_command(abort_request)
    
    def _execute_blob_start(self, channelID: BlobId):
        blob_start_data = bytearray()
        blob_start_data.append(BlobCommands.Blob_Start)
        blob_start_data.extend(channelID.value.to_bytes(2, byteorder='big', signed=True))
        start_request = self._request_builder._set_device_parameter_value(blob_start_data, 50, 0, _READ_BLOB_DATA_CID)
        self._execute_command(start_request)

    def _execute_blob_finish(self):
        finish_request = self._request_builder._set_device_parameter_value(BlobCommands.Blob_Finish, 50, 0, _READ_BLOB_DATA_CID)
        self._execute_command(finish_request)
    
    #more like a helper class that executes signals any errors
    def _execute_command(self, request, optional_client=None):
        cmd = BaseCommand(self._master_url, "", request)
        if optional_client is not None:
            cmd.attach_client(optional_client)
        response = cmd.execute()
        response_code = int(response["code"])
        if response_code != 200:
            message_str =f"Failed to send command with payload{str(request)} Aborting with code {str(response_code)}"
            error_code = int(response.get("error","0"),16)
            if error_code != 0:
                message_str += f" and error code {hex(error_code)}"
            raise ValueError(message_str)
        return response