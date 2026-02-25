import configparser

import pytest

pytest.importorskip("msal")

from pydag.services.office.MSGraphService import MSGraphService, MSGraphType


@pytest.mark.skip("requires user interaction via browser")
def test_000():
    
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    ms = MSGraphService(msgraph_type=MSGraphType.DEVICE_FLOW.value,
                        client_id = config["MS-GRAPH"]["client_id"],
                        tenant_id=config["MS-GRAPH"]["tenant_id"],
                        client_secret=config["MS-GRAPH"]["client_secret"]
                    )
    
    ms.install()
    
    ms.start()
    
    print (ms.me())
