import configparser
from datetime import date, datetime, timedelta, time
import uuid


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
    
def test_sendmail():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MS-GRAPH-AUTOMATE"):
        pytest.skip("Skipping MS Graph regression test: missing [MS-GRAPH-AUTOMATE] in config.ini")
    
    ms = MSGraphService(msgraph_type=MSGraphType.CLIENT.value,
                        client_id = config["MS-GRAPH-AUTOMATE"]["client_id2"],
                        tenant_id=config["MS-GRAPH-AUTOMATE"]["tenant_id2"],
                        client_secret=config["MS-GRAPH-AUTOMATE"]["client_secret2"]
                    )
    
    ms.install()    
    ms.start()    
    ms.sendmail(config["MS-GRAPH-AUTOMATE"]["user_mail1"], "Test Subject", "Test Body", [config["GMX"]["test_mail"]])

def test_create_calendar():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MS-GRAPH-AUTOMATE"):
        pytest.skip("Skipping MS Graph regression test: missing [MS-GRAPH-AUTOMATE] in config.ini")
    
    ms = MSGraphService(msgraph_type=MSGraphType.CLIENT.value,
                        client_id = config["MS-GRAPH-AUTOMATE"]["client_id2"],
                        tenant_id=config["MS-GRAPH-AUTOMATE"]["tenant_id2"],
                        client_secret=config["MS-GRAPH-AUTOMATE"]["client_secret2"]
                    )
    
    ms.install()
    
    ms.start()
    
    id = ms.create_calendar(config["MS-GRAPH-AUTOMATE"]["user_mail1"], "Test-Calendar")
    print(id)
    
def test_get_calendar_by_name():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MS-GRAPH-AUTOMATE"):
        pytest.skip("Skipping MS Graph regression test: missing [MS-GRAPH-AUTOMATE] in config.ini")
    
    ms = MSGraphService(msgraph_type=MSGraphType.CLIENT.value,
                        client_id = config["MS-GRAPH-AUTOMATE"]["client_id2"],
                        tenant_id=config["MS-GRAPH-AUTOMATE"]["tenant_id2"],
                        client_secret=config["MS-GRAPH-AUTOMATE"]["client_secret2"]
                    )
    
    ms.install()
    
    ms.start()
    
    id = ms.get_calendar_by_name(config["MS-GRAPH-AUTOMATE"]["user_mail1"], "Test-Calendar")
    print(id)
    
def test_create_event():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MS-GRAPH-AUTOMATE"):
        pytest.skip("Skipping MS Graph regression test: missing [MS-GRAPH-AUTOMATE] in config.ini")
    
    ms = MSGraphService(msgraph_type=MSGraphType.CLIENT.value,
                        client_id = config["MS-GRAPH-AUTOMATE"]["client_id2"],
                        tenant_id=config["MS-GRAPH-AUTOMATE"]["tenant_id2"],
                        client_secret=config["MS-GRAPH-AUTOMATE"]["client_secret2"]
                    )
    
    ms.install()    
    ms.start()
    
    user_id = config["MS-GRAPH-AUTOMATE"]["user_mail1"]
    cal_name = "Test-Calendar"
    cid = ms.get_calendar_by_name(config["MS-GRAPH-AUTOMATE"]["user_mail1"], cal_name)
    t = date.today() + timedelta(days=1)
    sdt = datetime.combine(t, time(hour=9, minute=30))
    edt = datetime.combine(t, time(hour=10, minute=30))   
    eid = ms.create_event(user_id, cid, "Test Event", "Test Description<br>More Text ...", sdt, edt)
    print(eid)
    
def test_create_event2():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MS-GRAPH-AUTOMATE"):
        pytest.skip("Skipping MS Graph regression test: missing [MS-GRAPH-AUTOMATE] in config.ini")
    
    ms = MSGraphService(msgraph_type=MSGraphType.CLIENT.value,
                        client_id = config["MS-GRAPH-AUTOMATE"]["client_id2"],
                        tenant_id=config["MS-GRAPH-AUTOMATE"]["tenant_id2"],
                        client_secret=config["MS-GRAPH-AUTOMATE"]["client_secret2"]
                    )
    
    ms.install()    
    ms.start()
    
    user_id = config["MS-GRAPH-AUTOMATE"]["user_mail1"]
    cal_name = "Test-Calendar"
    cid = ms.get_calendar_by_name(config["MS-GRAPH-AUTOMATE"]["user_mail1"], cal_name)
    t = date.today() + timedelta(days=1)
    sdt = datetime.combine(t, time(hour=16, minute=30))
    edt = datetime.combine(t, time(hour=17, minute=30))   
    eid = ms.create_event(user_id, cid, "Test Event", "Test Description<br>More Text ...", sdt, edt, 60)
    print(eid)
    
def test_create_event3():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("MS-GRAPH-AUTOMATE"):
        pytest.skip("Skipping MS Graph regression test: missing [MS-GRAPH-AUTOMATE] in config.ini")
    
    ms = MSGraphService(msgraph_type=MSGraphType.CLIENT.value,
                        client_id = config["MS-GRAPH-AUTOMATE"]["client_id2"],
                        tenant_id=config["MS-GRAPH-AUTOMATE"]["tenant_id2"],
                        client_secret=config["MS-GRAPH-AUTOMATE"]["client_secret2"]
                    )
    
    ms.install()    
    ms.start()
    
    user_id = config["MS-GRAPH-AUTOMATE"]["user_mail1"]
    cal_name = "Test-Calendar"
    cid = ms.get_calendar_by_name(config["MS-GRAPH-AUTOMATE"]["user_mail1"], cal_name)
    t = date.today() + timedelta(days=2)
    sdt1 = datetime.combine(t, time(hour=10, minute=30))
    edt1 = datetime.combine(t, time(hour=12, minute=30))
    uuid1 = str(uuid.uuid4())
    eid1 = ms.create_event(user_id, cid, "Test Event1", "Test Description<br>More Text ...", sdt1, edt1, external_id=uuid1)
    print(eid1)
    uuid2 = str(uuid.uuid4())
    sdt2 = datetime.combine(t, time(hour=8, minute=30))
    edt2 = datetime.combine(t, time(hour=11, minute=30))
    eid2 = ms.create_event(user_id, cid, "Test Event2", "Test Description<br>More Text ...", sdt2, edt2, external_id=uuid2)
    print(eid2)
    eid_found = ms.get_event_by_external_id(user_id, cid, uuid2)
    print(f"Found event id: {eid_found}")