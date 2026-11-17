import json
import os
import time

import requests

from pydag.buffers.DictBuffer import DictBuffer
from pydag.services.ThreadType import ThreadType
from pydag.services.iolink.IOLinkService import IOLinkService
    
def test_iolink_service_read_from_source():    
    d = DictBuffer()
    d.install()
    
    host = "http://192.168.1.250"
    iodd_path = os.path.dirname(__file__) + os.sep + "IODD_VVB301.xml"
    scaling = {"Temperature": 0.1, "Fatigue (v-RMS)": 0.0001, "Friction (a-RMS)": 0.01}    
    ios = IOLinkService(host=host, iodd_path=iodd_path, port=1, thread_type=ThreadType.MILLI_SECOND.value, scaling=scaling)
    ios.add_buffer(d)
    ios.install()
    
    print(ios._pdin_schema)
    
    for i in range(10):
        ios.read_from_source()
        
        print(d.data(persistent=False, n=1))
        time.sleep(0.1)


MASTER_IP = "192.168.1.250"
PORT = 1                  # X01
BASE_URL = f"http://{MASTER_IP}"
session = requests.Session()
session.timeout = 15
        
def test_iolink_blob():
    print("\nConnecting to ifm AL1340...")

    # Identify connected device
    for name in ["productname", "vendorid", "deviceid"]:

        result = api_request(
            f"/iolinkmaster/port[{PORT}]/iolinkdevice/{name}/getdata",
            method="GET"
        )

        print(f"{name}: {result['data']['value']}")

    print("\nReading VVB301 parameters...")

    # request blob transfer
    data = {
            "index": 2,
            "subindex": 0,
            "value": "DC"
        }

    result = api_request(f"/iolinkmaster/port[{PORT}]/iolinkdevice/iolwriteacyclic", method="POST", data=data)
    print(result)
    
    # Index 49: BLOB ID
    blob_id = read_parameter(49)
    
    # Index 8016: Raw data memory selection
    memory = read_parameter(8016)

    # Index 8017: Raw data trigger configuration
    trigger = read_parameter(8017)

    print("BLOB ID (index 49):", blob_id)
    print("Memory selection (8016):", memory)
    print("Trigger configuration (8017):", trigger)
    
    #for i in range(30):
    #    blob_id = read_parameter(49)
    #    print(f"{i * 0.5:.1f}s -> BLOB ID: {blob_id}")
    #    time.sleep(0.5)

    trigger = read_parameter(8017, 0)
    print(f"8017.0 -> {trigger}")
    trigger = read_parameter(8017, 1)
    print(f"8017.1 -> {trigger}")
    trigger = read_parameter(8017, 2)
    print(f"8017.2 -> {trigger}")
    
    #cmd = read_parameter(2, 0)
    #print(cmd)
    
    for index, sub in [(8017, 3), (8020, 0), (49, 0)]:
        result = read_parameter(index, sub)
        print(f"Index {index}.{sub}: {result}")

    # Explore the AL1340 IoT Core tree
    print("\nDiscovering available BLOB services...")

    try:
        tree = api_request("/gettree")
        tree_text = json.dumps(tree, indent=2)

        for line in tree_text.splitlines():
            if "blob" in line.lower():
                print(line.strip())

    except Exception as error:
        print("Tree discovery unavailable:", error)

    print("\nDiagnostic completed.")

def test_read_blob():
    # Step 1: Check that triggered raw data exists
    print("\nChecking raw data availability...")

    result = read_parameter(8020)
    print(result)


    # Step 2: Start BLOB transfer
    # F1 = BLOB_Start
    # EC75 = -5003

    print("\nStarting VVB301 BLOB transfer...")

    write_parameter(50, "F1EC75")


    # Step 3: Read BLOB information block

    print("\nReading BLOB information...")

    result = read_parameter(50)
    print(result)
    
def api_request(address, method="GET", data=None):

    if method == "GET":
        response = session.get(
            BASE_URL + address,
            timeout=15
        )

        response.raise_for_status()

        result = response.json()

        if result.get("code") != 200:
            raise RuntimeError(
                f"REST API error: {result}"
            )

        return result
    else:
        payload = {
            "code": "request",
            "cid": 4711,
            "adr": address
        }

        if data is not None:
            payload["data"] = data

        response = session.post(
            BASE_URL,
            json=payload,
            timeout=15
        )

        response.raise_for_status()

        result = response.json()

        if result.get("code") != 200:
            raise RuntimeError(
                f"REST API error: {result}"
            )

        return result

# ==========================================
# READ IO-LINK PARAMETER
# ==========================================

def read_parameter(index, subindex=0):

    address = (
        f"/iolinkmaster/port[{PORT}]"
        "/iolinkdevice/iolreadacyclic"
    )

    result = api_request(
        address,
        method="POST",
        data={
            "index": index,
            "subindex": subindex
        }
    )

    return result["data"]["value"]


# ==========================================
# WRITE IO-LINK PARAMETER
# ==========================================

def write_parameter(index, value, subindex=0):

    address = (
        f"/iolinkmaster/port[{PORT}]"
        "/iolinkdevice/iolwriteacyclic"
    )

    return api_request(
        address,
        method="POST",
        data={
            "index": index,
            "subindex": subindex,
            "value": value
        }
    )
