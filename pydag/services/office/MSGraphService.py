from dataclasses import dataclass, field
from datetime import datetime
import enum
import time
import webbrowser

import requests
from loguru import logger

from ..webserver.HttpHTMLService import HttpHTMLService
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

EXTERNAL_ID_UUID : str = "String {66f5a359-4659-4830-9070-00040ec6ac6e} Name externalId"

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
        if self.msgraph_type == MSGraphType.CLIENT.value and not self.client_secret:
            raise ServiceException("Client secret is required for client credentials flow")
        import msal

        match self.msgraph_type:
            case MSGraphType.CLIENT.value:                
                self._authority = f"{MICROSOFT_LOGIN_URL}/{self.tenant_id}"
                self._scope = [GRAPH_DEFAULT_SCOPE_URL]
                self._app = msal.ConfidentialClientApplication(
                    self.client_id,
                    authority=self._authority,
                    client_credential=self.client_secret,
                )
            case MSGraphType.USER.value:                
                self._authority = f"{MICROSOFT_LOGIN_URL}/common"
                self._scope = [ "User.Read",
                                "Mail.Read",
                                "Mail.Send"
                              ]
                self._app = msal.PublicClientApplication(
                    self.client_id,
                    authority=self._authority,
                )
            case MSGraphType.DEVICE_FLOW.value:
                self._authority = f"{MICROSOFT_LOGIN_URL}/{self.tenant_id}"
                self._scope = [ "User.Read",
                                "Mail.Read",
                                "Mail.Send"
                              ]
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
                            <div>Please enter the following device code in the sign-in window</div>
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
        if not response.ok:
            logger.error(
                "Graph request failed: status={} body={}",
                response.status_code,
                response.text,
            )
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint, data) -> dict:
        """POST request to Microsoft Graph API."""
        url = f"{GRAPH_API_URL}{endpoint}"
        response = requests.post(url, headers=self._headers(), json=data, timeout=self.timeout)
        if not response.ok:
            logger.error(f"Graph request failed: status={response.status_code} body={response.text}")
            logger.error(f"Headers: {response.headers}")
        response.raise_for_status()
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return response.text

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
        return response.json()
    
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
                "toRecipients": addresses                
            },
            "saveToSentItems": True
        }
        self._post("/me/sendmail", data)
    
    def users(self) -> dict:
        """ retrieve the users related to this sign-in

        Returns:
            dict: json user output
        """
        return self._get("/users")
    
    def sendmail(self, user_id : str, subject : str, body : str, recipients : list[str]):
        """ send a mail from specified `user_id` account """
        addresses = [{"emailAddress": {"address": e}} for e in recipients]
        data = {
            "message": {
                "subject": subject,
                "body": { "contentType": "Text", "content": body},
                "toRecipients": addresses                
            },
            "saveToSentItems": True
        }
        self._post(f"/users/{user_id}/sendMail", data)
    
    def create_calendar(self, user_id : str, calendar_name : str) -> str:
        """Create a calendar for the specified user.

        Args:
            user_id: The user's Microsoft Graph ID or email address.
            calendar_name: The name of the calendar to create.

        Returns:
            The created calendar's ID, or `None` if the creation failed.
        """        
        data = {
            "name": calendar_name
        }
        response : dict = self._post(f"/users/{user_id}/calendars", data)
        return response.get("id", None)
    
    def get_calendar_by_name(self, user_id : str, calendar_name : str) -> str:
        """Retrieve a user's calendar by name, following paginated results.

        Args:
            user_id: The user's Microsoft Graph ID or email address.
            calendar_name: The name of the calendar to find.

        Returns:
            The matching calendar id, or ``None`` if no calendar matches.
        """
        
        endpoint : str = f"/users/{user_id}/calendars?$select=id,name"
        while endpoint:            
            data = self._get(endpoint)

            for calendar in data.get("value", []):
                if calendar["name"] == calendar_name:
                    return calendar["id"]

            # Handle pagination
            endpoint = data.get("@odata.nextLink").replace(GRAPH_API_URL, "")
            
    def create_event(self, user_id : str, calendar_id : str, subject : str, body : str, start : datetime, end : datetime, reminder_minutes_before_start : int = 0, tz_start : str = "Europe/Berlin", tz_end : str = "Europe/Berlin", external_id : str = None) -> str:
        """Create an event in a user's calendar.

        Args:
            user_id: The user's Microsoft Graph ID or email address.
            calendar_id: The ID of the calendar where the event is created.
            subject: The event subject.
            body: The event body, interpreted as HTML.
            start: The event start date and time.
            end: The event end date and time.
            reminder_minutes_before_start: Minutes before the start to show a
                reminder, or ``None`` to disable the reminder.
            tz_start: Time zone for the start time.
            tz_end: Time zone for the end time.

        Returns:
            The created event's ID, or ``None`` if creation failed.
        """
        
        data = {
            "subject": subject,
            "start": {
                "dateTime": start.strftime("%Y-%m-%dT%H:%M:%S.%f") + "0",
                "timeZone": tz_start
            },
            "end": {
                "dateTime": end.strftime("%Y-%m-%dT%H:%M:%S.%f") + "0",
                "timeZone": tz_end
            },
            "body": {
                "contentType": "html",
                "content": body
            },
            "reminderMinutesBeforeStart": reminder_minutes_before_start,
            "isReminderOn": True if reminder_minutes_before_start > 0 else False                
        }
        if external_id:
            data["singleValueExtendedProperties"] = [
                    {
                        "id": f"{EXTERNAL_ID_UUID}",
                        "value": external_id
                    }
                ]
        response = self._post(f"/users/{user_id}/calendars/{calendar_id}/events", data)
        return response.get("id", None)
    
    def get_event_by_external_id(self, user_id : str, calendar_id : str, external_id : str) -> str:
        params = {
            "$filter": (
                "singleValueExtendedProperties/Any("
                f"ep: ep/id eq '{EXTERNAL_ID_UUID}' and ep/value eq '{external_id}'"
                ")"
            ),
            "$expand": (
                "singleValueExtendedProperties("
                f"$filter=id eq '{EXTERNAL_ID_UUID}'"
                ")"
            )
        }
        response = self._get(f"/users/{user_id}/calendars/{calendar_id}/events", params)
        return response.get("value", [])[0].get("id", None)
        
    
    def get_events_by_filter(self, user_id : str, calendar_id : str, filter : str) -> list[str]:
        params = {
            "$filter": filter
        }
        response = self._get(f"/users/{user_id}/calendars/{calendar_id}/events", params)
        return response.get("value", []) 