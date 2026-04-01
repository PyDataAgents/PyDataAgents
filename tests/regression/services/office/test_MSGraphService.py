import configparser

import pytest
from pydag.services.office.MSGraphService import MSGraphService, MSGraphType


def test_000():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MS-GRAPH"):
        pytest.skip("Skipping MS Graph regression test: missing [MS-GRAPH] in config.ini")
    for key in ("client_id", "tenant_id", "client_secret"):
        if not config.has_option("MS-GRAPH", key):
            pytest.skip(f"Skipping MS Graph regression test: missing {key} in [MS-GRAPH] of config.ini")
    
    ms = MSGraphService(msgraph_type=MSGraphType.DEVICE_FLOW.value,
                        client_id = config["MS-GRAPH"]["client_id"],
                        tenant_id=config["MS-GRAPH"]["tenant_id"],
                        client_secret=config["MS-GRAPH"]["client_secret"]
                    )
    
    ms.install()
    
    ms.start()
    
    print (ms.me())
