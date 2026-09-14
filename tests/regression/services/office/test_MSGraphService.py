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
    
def test_001():
    
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
    print (ms.me_messages())
    
    
def test_010():
    
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
    
    print (ms.users())
    
def test_020():
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
    
    ms.sendmail("17c367a9-ad94-4c79-a86f-07f28d8a3b64", "Test Subject", "Test Body", [config["GMX"]["test_mail"]])
    
    
def test_030():
    import msal
    import requests
    config = configparser.ConfigParser()
    config.read("config.ini")
    CLIENT_ID = config["MS-GRAPH"]["client_id"]
    TENANT_ID=config["MS-GRAPH"]["tenant_id"]
    
    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority="https://login.microsoftonline.com/consumers",
    )

    result = app.acquire_token_interactive(
        scopes=[
            "User.Read",
            "Mail.Read",
            "Mail.Send",
        ]
    )

    if "access_token" not in result:
        raise RuntimeError(result)
    
    response = requests.get(
        "https://graph.microsoft.com/v1.0/me/messages",
        headers={
            "Authorization": f"Bearer {result['access_token']}",
        },
    )

    print(response.status_code)
    print(response.text)
    
def test_040():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MS-GRAPH"):
        pytest.skip("Skipping MS Graph regression test: missing [MS-GRAPH] in config.ini")
    for key in ("client_id", "tenant_id", "client_secret"):
        if not config.has_option("MS-GRAPH", key):
            pytest.skip(f"Skipping MS Graph regression test: missing {key} in [MS-GRAPH] of config.ini")
    
    ms = MSGraphService(msgraph_type=MSGraphType.CLIENT.value,
                        client_id = config["MS-GRAPH-AUTOMATE"]["client_id2"],
                        tenant_id=config["MS-GRAPH-AUTOMATE"]["tenant_id2"],
                        client_secret=config["MS-GRAPH-AUTOMATE"]["client_secret2"]
                    )
    
    ms.install()
    
    ms.start()
    
    ms.sendmail("hillenbrand@automate-shw.de", "Test Subject", "Test Body", [config["GMX"]["test_mail"]])
