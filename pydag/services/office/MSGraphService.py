from dataclasses import dataclass, field
import enum
import time
import webbrowser

import requests

from ...services.documents.HttpHTMLService import HttpHTMLService
from ...agents.Agent import Agent
from ...services.ServiceException import ServiceException
from ...services.Service import Service


class MSGraphType(str, enum.Enum):
    CLIENT = "client"
    USER = "user"
    DEVICE_FLOW = "device-flow"

GRAPH_API_URL : str = "https://graph.microsoft.com/v1.0"
MICROSOFT_LOGIN_URL : str = "https://login.microsoftonline.com"
GRAPH_DEFAULT_SCOPE_URL : str = "https://graph.microsoft.com/.default"

@dataclass
class MSGraphService(Service):
    """ `Service` that provieds functionalities to access Microsoft Graph API

    """
    
    client_id : str = field(default=None, metadata={"description": "client id for the msgraph api"})
    tenant_id : str = field(default=None, metadata={"description": "tenant id for the msgraph api"})
    client_secret : str = field(default=None, metadata={"description": "client secret for the msgraph api"})
    msgraph_type : str = field(default=MSGraphType.CLIENT.value, metadata={"description": "client secret for the msgraph api"})
    timeout : float = field(default=10, metadata={"description": "timeout for api calls in seconds"})

    def __post_init__(self):
        super().__post_init__()
        self._app = None
        self._token : dict = None
        self._scope : list[str] = None
        self._authority : str = None
        
    def _on_install(self, agent : Agent = None):
        super()._on_install(agent)
        self._authority = f"{MICROSOFT_LOGIN_URL}/{self.tenant_id}"
        self._scope = [GRAPH_DEFAULT_SCOPE_URL] if self.msgraph_type == MSGraphType.CLIENT.value else ["User.Read"]
        if self.msgraph_type == MSGraphType.CLIENT.value and not self.client_secret:
            raise ServiceException("Client secret is required for client credentials flow")
        import msal

        if self.msgraph_type == MSGraphType.CLIENT.value:
            self._app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self._authority,
                client_credential=self.client_secret,
            )
        else:
            self._app = msal.PublicClientApplication(
                self.client_id,
                authority=self._authority,
            )
                
    def _on_start(self):       
        self._authenticate()
    
    def _on_stop(self):
        self._app = None
        self._token = None
    
    def _authenticate(self):
        """Authenticate and acquire an access token."""        
        match self.msgraph_type:
            case MSGraphType.CLIENT.value:
                result = self._app.acquire_token_for_client(scopes=self._scope)
            case MSGraphType.USER.value:
                result = self._app.acquire_token_interactive(scopes=self._scope)
            case MSGraphType.DEVICE_FLOW.value:
                flow = self._app.initiate_device_flow(scopes=self._scope)
                #print(flow)
                # Opens the URL in the default browser
                webbrowser.open(flow["verification_uri"])
                
                html = f"""
                    <html>
                        <head>
                            <title>Device Code</title>
                        </head>
                        <body>
                            <h1>Device Code</h1>
                            <div>Please enter the following devic code in the sign-in window</div>
                            <h4>{flow["user_code"]}</h4>
                        </body>
                    </html>    
                """
                
                html_service = HttpHTMLService(port=8099, html=html)
                html_service.install()
                html_service.start()  
                time.sleep(2)                             
                webbrowser.open(f"http://localhost:{html_service.port}")                
                time.sleep(2)
                html_service.stop()
                                
                #print(flow["message"])  # visit URL, enter code
                result = self._app.acquire_token_by_device_flow(flow)
                #print(result["access_token"])

        if "access_token" in result:
            self._token = result["access_token"]
        else:
            raise ServiceException(f"Authentication failed: {result.get('error_description')}")    
    
    def _headers(self) -> dict:
        if not self._token:
            self._authenticate()
        return {"Authorization": f"Bearer {self._token}"}    
    
    def _get(self, endpoint, params=None) -> dict:
        """GET request to Microsoft Graph API."""
        url = f"{GRAPH_API_URL}{endpoint}"
        response = requests.get(url, headers=self._headers(), params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint, data) -> dict:
        """POST request to Microsoft Graph API."""
        url = f"{GRAPH_API_URL}{endpoint}"
        response = requests.post(url, headers=self._headers(), json=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def _patch(self, endpoint, data) -> dict:
        """PATCH request to Microsoft Graph API."""
        url = f"{GRAPH_API_URL}{endpoint}"
        response = requests.patch(url, headers=self._headers(), json=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def _delete(self, endpoint) -> dict:
        """DELETE request to Microsoft Graph API."""
        url = f"{GRAPH_API_URL}{endpoint}"
        response = requests.delete(url, headers=self._headers(), timeout=self.timeout)
        response.raise_for_status()
        return response.status_code == 204
    
    def me(self) -> dict:
        """ get personal info of signed-in user

        Returns:
            dict: json output
        """
        return self._get("/me")
    
    def me_messages(self) -> dict:
        """ get emails from signed-in user

        Returns:
            dict: json message output
        """
        return self._get("/me/messages")
        
    def me_sendmail(self, subject : str, body : str, recipients : list[str]):
        """ send a mail from signed-in account
        
        Args:
            subject (str): mail subject
            body (str): mail body
            recipients (list[str]): list of email addresses
        """
        addresses = [{"emailAddress": {"address": e}} for e in recipients]
        data = {
            "message": {
                "subject": subject,
                "body": { "contentType": "Text", "content": body},
                "toRecipients": [addresses]                
            },
            "saveToSentItems": "true"
        }
        self._post("/me/sendmail", data)
    
    def users(self) -> dict:
        """ retrieve the users related to this sign-in

        Returns:
            dict: json user output
        """
        return self._get("/users")
    
    
    
