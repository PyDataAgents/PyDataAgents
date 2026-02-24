import requests


class SAPODataClient:
    def __init__(
        self,
        base_url,
        username,
        password,
        verify_ssl=True
    ):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = verify_ssl
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, payload):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()