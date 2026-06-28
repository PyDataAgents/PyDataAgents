import configparser
import re
import requests
from msal import ConfidentialClientApplication

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
    
    
def test_010():
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    TENANT_ID = config["MS-GRAPH-AUTOMATE"]["tenant_id"]
    CLIENT_ID = config["MS-GRAPH-AUTOMATE"]["client_id"]
    CLIENT_SECRET = config["MS-GRAPH-AUTOMATE"]["client_secret"]

    TEAM_ID = "fdf18d4f-8029-4dbf-8c7f-316f8fd49eb1"
    CHANNEL_ID = "19:f46558cbf0394213a097fbf5252f64e4@thread.tacv2"
    #https://teams.cloud.microsoft/l/channel/19%3Af46558cbf0394213a097fbf5252f64e4%40thread.tacv2/SalesOfferComparisonChat?groupId=fdf18d4f-8029-4dbf-8c7f-316f8fd49eb1&tenantId=6048b131-a26b-4611-89f3-04b969c1059b

    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    SCOPE = ["https://graph.microsoft.com/.default"]

    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )

    token = app.acquire_token_for_client(scopes=SCOPE)

    headers = {
        "Authorization": f"Bearer {token['access_token']}"
    }

    channel_msg_url = f"https://graph.microsoft.com/v1.0/teams/{TEAM_ID}/channels/{CHANNEL_ID}/messages"

    response = requests.get(channel_msg_url, headers=headers, timeout=10)
    messages = response.json()

    for msg in messages.get("value", []):
        msg_id = msg["id"]
        content = msg["body"]["content"]
        ts =  msg["createdDateTime"]
        print(msg_id, ts, content)
        re.findall(r'<attachment id="(.*?)"', content or "")
        
