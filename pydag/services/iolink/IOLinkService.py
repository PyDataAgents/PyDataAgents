from dataclasses import dataclass, field
import json
import zipfile
import xml.etree.ElementTree as ET

import urllib3

from pydag.agents.Agent import Agent
from pydag.buffers.Buffer import Buffer
from pydag.services.ReadService import ReadService

VVB301_SCHEMA = {
    "bit_length": 128,
    "byte_order": "big",
    "fields": [
        {
            "name": "v_rms",
            "offset": 112,
            "length": 16,
            "type": "int",
            "exponent_from": "v_rms_exponent",
        },
        {
            "name": "v_rms_exponent",
            "offset": 104,
            "length": 8,
            "type": "int",
        },
        {
            "name": "v_axis",
            "offset": 100,
            "length": 4,
            "type": "uint",
        },
        {
            "name": "a_peak",
            "offset": 80,
            "length": 16,
            "type": "int",
            "exponent_from": "a_exponent",
        },
        {
            "name": "a_rms",
            "offset": 64,
            "length": 16,
            "type": "int",
            "exponent_from": "a_exponent",
        },
        {
            "name": "a_exponent",
            "offset": 56,
            "length": 8,
            "type": "int",
        },
        {
            "name": "a_axis",
            "offset": 52,
            "length": 4,
            "type": "uint",
        },
        {
            "name": "crest",
            "offset": 32,
            "length": 16,
            "type": "int",
            "scale": 0.1,
            "invalid": [32760, 32764],
        },
        {
            "name": "temperature",
            "offset": 16,
            "length": 16,
            "type": "int",
            "exponent_from": "temperature_exponent",
            "invalid": [-32760, 32760, 32764],
        },
        {
            "name": "temperature_exponent",
            "offset": 8,
            "length": 8,
            "type": "int",
        },
        {
            "name": "device_status",
            "offset": 4,
            "length": 4,
            "type": "uint",
        },
        {
            "name": "unbalance",
            "offset": 3,
            "length": 1,
            "type": "bool",
        },
        {
            "name": "v_ou1",
            "offset": 2,
            "length": 1,
            "type": "bool",
        },
        {
            "name": "out2",
            "offset": 1,
            "length": 1,
            "type": "bool",
        },
        {
            "name": "out1",
            "offset": 0,
            "length": 1,
            "type": "bool",
        },
    ]
}

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
    def _parse_iodd_schema(iodd_path : str, process_data_id: str = "PDIn") -> dict:
        """
        Parses an IO-Link IODD zip file, extracts process data fields, 
        automatically maps 'exponent_from' relationships, and retrieves invalid value codes.
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

        root = ET.fromstring(xml_content)
        
        def strip_ns(tag):
            return tag.split('}')[-1] if '}' in tag else tag

        # 2. Extract text mappings (to resolve human-readable names from TextIds)
        texts = {}
        datatypes = {}
        
        for elem in root.iter():
            tag = strip_ns(elem.tag)
            if tag in ('PrimaryLanguage', 'Text'):
                t_id = elem.get('id')
                value = elem.get('value')
                if t_id and value:
                    texts[t_id] = value
            elif tag == 'DatatypeCollection':
                for dt in elem:
                    dt_id = dt.get('id')
                    if dt_id:
                        datatypes[dt_id] = dt

        def resolve_name(elem):
            for attr in ['name', 'id']:
                val = elem.get(attr)
                if val in texts:
                    return texts[val]
                if val:
                    return val
            text_id = elem.get('textId')
            if text_id in texts:
                return texts[text_id]
            return "unknown_field"

        # 3. Locate target ProcessData element
        pd_collection = None
        for elem in root.iter():
            if strip_ns(elem.tag) == 'ProcessDataCollection':
                pd_collection = elem
                break

        if pd_collection is None:
            raise ValueError("ProcessDataCollection not found in IODD XML.")

        target_pd = None
        for pd in pd_collection:
            if strip_ns(pd.tag) == 'ProcessData' and pd.get('id') == process_data_id:
                target_pd = pd
                break
                
        if target_pd is None:
            for pd in pd_collection:
                if strip_ns(pd.tag) == 'ProcessData':
                    target_pd = pd
                    break

        if target_pd is None:
            raise ValueError(f"ProcessData '{process_data_id}' not found.")

        bit_length = int(target_pd.get('bitLength', 0))
        fields = []

        # 4. Resolve Datatype structure (RecordT)
        datatype_elem = None
        for child in target_pd:
            tag = strip_ns(child.tag)
            if tag == 'RecordT':
                datatype_elem = child
                break
            elif 'Ref' in tag:
                ref_id = child.get('datatypeId') or child.get('idRef')
                if ref_id in datatypes:
                    datatype_elem = datatypes[ref_id]

        if datatype_elem is None:
            for child in target_pd.iter():
                if strip_ns(child.tag) == 'RecordT':
                    datatype_elem = child
                    break

        # 5. Parse individual fields (RecordItems) & constraints
        raw_fields = []
        if datatype_elem is not None:
            for item in datatype_elem:
                if strip_ns(item.tag) == 'RecordItem':
                    name = resolve_name(item)
                    bit_length_item = int(item.get('bitLength', 1))
                    bit_offset_item = int(item.get('bitOffset', 0))

                    field_type = "uint"
                    scale = None
                    invalid_values = []

                    for sub in item:
                        sub_tag = strip_ns(sub.tag)
                        if 'Integer' in sub_tag and 'U' not in sub_tag:
                            field_type = "int"
                        elif 'UInteger' in sub_tag:
                            field_type = "uint"
                        elif 'Boolean' in sub_tag:
                            field_type = "bool"
                        elif 'Float' in sub_tag:
                            field_type = "float"
                            
                        gradient = sub.get('gradient')
                        if gradient:
                            try:
                                scale = float(gradient)
                            except ValueError:
                                pass
                        
                        # Look for error / invalid code definitions (e.g., SingleValue constraints)
                        for constraint in sub.iter():
                            if strip_ns(constraint.tag) == 'SingleValue':
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

        # 6. Post-Processing: Automatically Map 'exponent_from' 
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