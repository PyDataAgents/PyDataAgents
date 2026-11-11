from pydag.agents.Agent import Agent
from pydag.agents.app.AgentApp import AgentApp
from pydag.nodes.http.HttpGetAction import HttpGetAction
from pydag.nodes.utils.ParseHexAction import ParseHexAction
from pydag.services.statemachine.SimpleStatemachine import SimpleStatemachine

URL = "http://192.168.1.250/iolinkmaster/port[1]/iolinkdevice/pdin/getdata"    
    

# 1. Define the continuous structural mapping string 
# >  = Big-Endian (Network Byte Order)
# h  = 2-byte signed short integer (16-bit)
# b  = 1-byte signed integer (8-bit)
# B  = 1-byte unsigned integer (8-bit)
# H  = 2-byte unsigned short integer (16-bit)

# 2. Define the exact ordered metric fields and their matching scaling factors
VVB301_SCHEMA = [
    {"name": "v_rms (Fatigue)",       "scale": 0.0001, "unit": "m/s"},
    {"name": "v_rms_scaling",         "scale": 1.0,    "unit": ""},
    {"name": "a_peak (Impact)",       "scale": 0.1,    "unit": "m/s²"},
    {"name": "a_rms (Friction)",      "scale": 0.1,    "unit": "m/s²"},
    {"name": "a_scaling",             "scale": 1.0,    "unit": ""},
    {"name": "crest_factor",          "scale": 0.1,    "unit": ""},
    {"name": "temperature",           "scale": 0.1,    "unit": "°C"},
    {"name": "crest_scaling",         "scale": 1.0,    "unit": "code"},
    {"name": "device_status",         "scale": 1.0,    "unit": "binary"}
]

STRUCT_SCHEMA = ">hhhhhhhBB"

SCALING = [0.0001, None, 0.1, 0.1, None, 0.1, 0.1, None, None]

OUTPUT_KEYS = ["V_RMS", "V_RMS_SCALING", "A_PEAK", "A_RMS", "A_SCALING", "CREST", "TEMP", "CREST_SCALING", "STATUS"]

def test_iolink_vvb301_sensor():
     
    hga = HttpGetAction(url=URL, json_path="data.value", output_keys=["hex_data"])
    hga.install()
    
    pha = ParseHexAction(input_keys=["values"], output_keys=OUTPUT_KEYS, schema=STRUCT_SCHEMA, scaling=SCALING)
    pha.add_parent(hga)
    pha.install()
    
    hga.execute()
    pha.execute()
    
    print(pha.get_data())
    

def test_iolink_vvb301_agent():
    
    ag = Agent()
    
    sm = SimpleStatemachine()
        
    hga = HttpGetAction(url=URL, json_path="data.value", output_keys="hex_data")
    sm.add_node(hga)
    
    
    pha = ParseHexAction(input_keys="hex_data", output_keys=OUTPUT_KEYS, schema=STRUCT_SCHEMA, scaling=SCALING)
    pha.add_parent(hga)
    sm.add_node(pha)   
    
    ag.add_service(sm)
    
    aa = AgentApp(agent=ag, with_ui=True)
    aa.create()
    aa.run()