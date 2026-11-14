from dataclasses import dataclass, field
import json
import zipfile
import xml.etree.ElementTree as ET

import urllib3

from pydag.agents.Agent import Agent
from pydag.buffers.Buffer import Buffer
from pydag.services.ReadService import ReadService
from pydag.services.ServiceException import ServiceException

@dataclass
class IOLinkService(ReadService):
    
    host : str = field(default=None, metadata={"description": ""})
    iodd_path : str = field(default=None, metadata={"description": ""})
    port : int = field(default=1, metadata={"description": ""})
    scaling : list[int] = field(default_factory=list, metadata={"description": ""})
    
    def __post_init__(self):
        super().__post_init__()
        self._pdin_schema : dict = None
        self._http : urllib3.PoolManager = None
    
    def _on_install(self, agent : Agent = None):
        super()._on_install()
        self._pdin_schema = IOLinkService._parse_iodd_schema(self.iodd_path)
        self._http = urllib3.PoolManager()
    
    def _on_uninstall(self, agent : Agent = None):
        super()._on_uninstall(agent)
        self._http = None
        
    def read_from_source(self):
        url : str = f"{self.host}/iolinkmaster/port[{self.port}]/iolinkdevice/pdin/getdata"
        if len(self.get_buffers()) == 1:
            buffer : Buffer = next(iter(self.get_buffers().values()))
            response = self._http.request("GET", url)
            body = response.data
            s = body.decode("utf-8")
            json_data = json.loads(s)
            hex_data = json_data["data"]["value"]
            d : dict = IOLinkService._decode_process_data(hex_data, self._pdin_schema)
            buffer.push(d)
    
    @staticmethod
    def _parse_iodd_schema(iodd_path : str) -> dict:
        """
        Parses an IO-Link IODD zip file, extracts process data fields, 
        automatically maps 'exponent_from' relationships, and retrieves invalid value codes.
        <br>
        The returned schema looks like this:
        <br>
        
        {
            "bit_length": 128,
            "byte_order": "big",
            "fields": [                
                {
                    "name": "crest",
                    "offset": 32,
                    "length": 16,
                    "type": "int",
                    "scale": 0.1,
                    "invalid": [32760, 32764],
                },
                ...
            ]
        }
        """
        xml_content = None

        # 1. Handle IODD ZIP archive or direct XML file
        if zipfile.is_zipfile(iodd_path):
            with zipfile.ZipFile(iodd_path, 'r') as z:
                xml_files = [f for f in z.namelist() if f.lower().endswith('.xml') and not f.lower().startswith('iodd-ml')]
                if not xml_files:
                    xml_files = [f for f in z.namelist() if f.lower().endswith('.xml')]
                if not xml_files:
                    raise ValueError("No XML files found inside the IODD archive.")
                
                main_xml = next((f for f in xml_files if 'iodd' in f.lower() or 'device' in f.lower() or len(xml_files) == 1), xml_files[0])
                with z.open(main_xml) as f:
                    xml_content = f.read()
        else:
            with open(iodd_path, 'rb') as f:
                xml_content = f.read()

        xml_tree = ET.fromstring(xml_content) 
        
        # remove namespace from xml
        for elem in xml_tree.iter():
            # Remove namespace from element tag
            if "}" in elem.tag:
                elem.tag = elem.tag.split("}", 1)[1]

            # Remove namespace from attribute names
            elem.attrib = {
                key.split("}", 1)[-1]: value
                for key, value in elem.attrib.items()
            }                      
        
        # Extract text mappings (to resolve human-readable names from TextIds)
        texts = {}
        datatypes = {}
                
        text_collection = xml_tree.find(".//PrimaryLanguage")
        
        for elem in text_collection:
            tag = elem.tag
            if tag == 'Text':
                t_id = elem.get('id')
                value = elem.get('value')
                if t_id and value:
                    texts[t_id] = value
        
        pd_collection = xml_tree.find(".//ProcessDataCollection")
        if pd_collection is None:
            raise ServiceException("ProcessDataCollection not found in IODD XML.")

        pd_in = pd_collection.find(".//ProcessDataIn")
        if pd_in is None:
            raise ServiceException("ProcessDataIn not found in IODD XML.")
            
        bit_length = int(pd_in.get('bitLength', 0))
        fields = []
        
        # Parse individual fields (RecordItems) & constraints        
        datatype_elem = pd_in.find(".//Datatype")
        if datatype_elem is None:
            raise ServiceException("Datatype Element was not found in ProcessDataIn IODD XML.")
        
        raw_fields = []
        for item in datatype_elem:
            if item.tag == 'RecordItem':
                name_elem = item.find("Name")
                if name_elem is not None:
                    name = name_elem.get("textId")
                    if name in texts:
                        name = texts[name]
                    
                    simple_dt_elem = item.find("SimpleDatatype")
                    bit_length_item = 0
                    bit_offset_item = 0   
                    if simple_dt_elem is not None:
                        bit_length_item = int(simple_dt_elem.get('bitLength', 0)) 
                        dt : str = simple_dt_elem.get("type", "UIntegerT")
                        field_type = IOLinkService._convert_datatype(dt)
                        if bit_length_item == 0 and field_type == "bool":
                            bit_length_item = 1
                    bit_offset_item = int(item.get('bitOffset', 0))
                                        
                    scale = None
                    invalid_values = []

                    for sub in item:  
                        gradient = sub.get('gradient')
                        if gradient:
                            try:
                                scale = float(gradient)
                            except ValueError:
                                pass
                        
                        # Look for error / invalid code definitions (e.g., SingleValue constraints)
                        for constraint in sub.iter():
                            if constraint.tag == 'SingleValue':
                                sv_id = constraint.get('id', '').lower()
                                # Check if the code represents an error, overload, or invalid state
                                if any(keyword in sv_id for keyword in ['err', 'inval', 'ov', 'no_val', 'not_a_number', 'dataloss']):
                                    val_str = constraint.get('value')
                                    if val_str:
                                        try:
                                            invalid_values.append(int(val_str))
                                        except ValueError:
                                            pass

                    field_entry = {
                        "name": name,
                        "offset": bit_offset_item,
                        "length": bit_length_item,
                        "type": field_type
                    }
                    if scale and scale != 1.0:
                        field_entry["scale"] = scale
                    if invalid_values:
                        field_entry["invalid"] = sorted(list(set(invalid_values)))

                    raw_fields.append(field_entry)

        # Sort fields descending by bit offset (standard big-endian arrangement)
        raw_fields.sort(key=lambda x: x["offset"], reverse=True)

        # Post-Processing: Automatically Map 'exponent_from' 
        field_names = {f["name"] for f in raw_fields}
        for field in raw_fields:
            expected_exponent_name = f"{field['name']}_exponent"
            if expected_exponent_name in field_names:
                field["exponent_from"] = expected_exponent_name

        return {
            "bit_length": bit_length,
            "byte_order": "big",
            "fields": raw_fields
        }
        
    @staticmethod    
    def _decode_process_data(hex_data: str, schema: dict) -> dict:
        """
        Decode IO-Link process data using a normalized schema.

        Supported types:
            uint, int, bool

        Supported field options:
            scale
            exponent_from
            invalid
        """

        hex_data = hex_data.replace(" ", "").replace("0x", "")

        if len(hex_data) % 2:
            raise ValueError("Hex data must contain complete bytes")

        byte_order = schema.get("byte_order", "big")
        raw_bytes = bytes.fromhex(hex_data)

        if len(raw_bytes) * 8 != schema["bit_length"]:
            raise ValueError(
                f"Expected {schema['bit_length']} bits, "
                f"received {len(raw_bytes) * 8}"
            )

        raw_integer = int.from_bytes(raw_bytes, byte_order)

        def extract(offset: int, length: int) -> int:
            shift = schema["bit_length"] - offset - length
            if shift < 0 or length <= 0:
                raise ValueError("Invalid field offset or length")

            return (raw_integer >> shift) & ((1 << length) - 1)

        def convert_signed(value: int, length: int) -> int:
            sign_bit = 1 << (length - 1)
            return value - (1 << length) if value & sign_bit else value

        # First pass: extract raw values.
        result = {}

        for field in schema["fields"]:
            name = field["name"]
            length = field["length"]

            value = extract(field["offset"], length)

            if field["type"] == "int":
                value = convert_signed(value, length)
            elif field["type"] == "bool":
                value = bool(value)
            elif field["type"] != "uint":
                raise ValueError(f"Unsupported type: {field['type']}")

            result[name] = value

        # Second pass: apply scaling and invalid-value handling.
        for field in schema["fields"]:
            name = field["name"]
            value = result[name]

            if value in field.get("invalid", []):
                result[name] = None
                continue

            if field["type"] == "bool":
                continue

            if "exponent_from" in field:
                exponent = result[field["exponent_from"]]
                if exponent is None:
                    result[name] = None
                    continue
                value *= 10 ** exponent

            value *= field.get("scale", 1)
            result[name] = value

        return result

    @staticmethod
    def _convert_datatype(iodd_datatype : str) -> str:
        match iodd_datatype:            
            case "UIntegerT":
                return "uint"
            case "BooleanT":
                return "bool"
            case "IntegerT":
                return "int"
            case _:
                return "uint"