import configparser

import pytest

from pydag.nodes.office.OutlookMailAction import OutlookMailAction
from pydag.services.office.MSGraphService import MSGraphService, MSGraphType


def test_outlook_mail():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MS-GRAPH"):
        pytest.skip("Skipping MS Graph regression test: missing [MS-GRAPH] in config.ini")
    for key in ("client_id", "tenant_id", "client_secret"):
        if not config.has_option("MS-GRAPH", key):
            pytest.skip(f"Skipping MS Graph regression test: missing {key} in [MS-GRAPH] of config.ini")
    
    ms = MSGraphService(msgraph_type=MSGraphType.CLIENT.value,
                        client_id = config["MS-GRAPH"]["client_id"],
                        tenant_id=config["MS-GRAPH"]["tenant_id"],
                        client_secret=config["MS-GRAPH"]["client_secret"]
                    )
    
    ms.install()
    ms.start()
    
    oa = OutlookMailAction(recipients=[config["GMX"]["test_mail"]], subject="Test Subject", body="Test Body<hr>Test Section")
    oa.set_service(ms)
    oa.install()
    oa.execute()