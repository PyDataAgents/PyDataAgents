import requests
from requests_ntlm import HttpNtlmAuth
import xml.etree.ElementTree as ET


def test_000():
    session = requests.Session()
    session.auth = HttpNtlmAuth("domain\user", "password")
    
    resp = session.get("http:/url")
    
    
    if resp.status_code == 200:
        # Get the content
        print(resp.content)
        root = ET.fromstring(resp.content)

        # Example: Print out tag names and text
        for child in root:
            print(child.tag, child.text)
    else:
        print(f"Request failed with status code {resp.status_code}")