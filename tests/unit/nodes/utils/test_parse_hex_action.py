from pydag.nodes.utils.ParseHexAction import ParseHexAction


def test_parse_hex_example1():
    
    # Create an instance of ParseHexAction with a schema and scaling factors
    parse_hex_action = ParseHexAction(schema='>Hf', scaling=[1.0, 0.1], output_keys=['field1', 'field2'])
    
    # Simulate the installation of the node
    parse_hex_action.install()
    
    # Simulate input data with a hexadecimal string
    input_data = [{'hex_string': '0001C248F5C3'}]  # Example hex string representing (1, -50.24)
    
    # Mock the get_parent_data method to return the input data
    parse_hex_action.get_parent_data = lambda by_rows: input_data
    
    # Execute the node to parse the hex string
    parse_hex_action.execute()
    
    # Retrieve the output data
    output_data = parse_hex_action.get_data()
    
    assert output_data["field1"][0] == 1
    assert round(output_data["field2"][0], 3) == -5.024 