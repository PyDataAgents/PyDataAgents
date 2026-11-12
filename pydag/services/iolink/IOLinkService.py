from dataclasses import dataclass, field

from pydag.services.MappingService import MappingService

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
    ],
}

@dataclass
class IOLinkService(MappingService):
    
    host : str = field()
    iodd_file : str = field()
    port : int = field()
    scaling : list[int] = field()
    
    def __post_init__(self):
        super().__post_init__()
        self._pdin_schema : dict = None
    
    @staticmethod
    def _parse_schema() -> dict:
        pass
        
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