from string import Template
from copy import deepcopy

_generic_device_template = {
 "code":"request",
 "cid":-1,
 "adr":"iolinkmaster/port[$port_number]/iolinkdevice/",
 }
 
_generic_request_template = {
 "code":"request",
 "cid":-1,
 "adr":"",
 }
 
 
def _get_bound_generic_device_request(iol_master_port, cid = None):
     bound_request = deepcopy(_generic_device_template)
     if cid is not None:
         bound_request["cid"] = cid
     temp_obj = Template(bound_request["adr"])
     bound_request["adr"] = temp_obj.substitute(port_number=iol_master_port)
     return bound_request
 
def get_device_ID_request(iol_master_port, cid = None):
     request = _get_bound_generic_device_request(iol_master_port, cid)
     request["adr"] += "deviceid/getdata"
     return request

def get_device_vendorid_ID_request(iol_master_port, cid = None):
     request = _get_bound_generic_device_request(iol_master_port, cid)
     request["adr"] += "vendorid/getdata"
     return request

def get_device_status_request(iol_master_port, cid = None):
     request = _get_bound_generic_device_request(iol_master_port, cid)
     request["adr"] += "status/getdata"
     return request

def get_tree_request(cid = None):
    request = deepcopy(_generic_request_template)
    if cid is not None:
        request["cid"] = cid
    request["adr"] = "gettree"
    return request

def get_process_data_request(iol_master_port, cid = None):
     request = _get_bound_generic_device_request(iol_master_port,cid)
     request["adr"] += "pdin/getdata"
     return request