from dataclasses import dataclass, field
from datetime import datetime
import enum
import time
from typing import Any
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
    
    def _get(self, endpoint, params=None) -> requests.Response:
        """GET request to Microsoft Graph API."""
        url = f"{GRAPH_API_URL}{endpoint}"
        response = requests.get(url, headers=self._headers(), params=params, timeout=self.timeout)
        if not response.ok:
            logger.error(f"Graph request failed: status={response.status_code} body={response.text}")
            logger.error(f"Headers: {response.headers}")
            return None
        else:
            return response

    def _post(self, endpoint, data) -> requests.Response:
        """POST request to Microsoft Graph API."""
        url = f"{GRAPH_API_URL}{endpoint}"
        response = requests.post(url, headers=self._headers(), json=data, timeout=self.timeout)
        if not response.ok:
            logger.error(f"Graph request failed: status={response.status_code} body={response.text}")
            logger.error(f"Headers: {response.headers}")
            return None
        else:
            return response

    def _patch(self, endpoint, data) -> requests.Response:
        """PATCH request to Microsoft Graph API."""
        url = f"{GRAPH_API_URL}{endpoint}"
        response = requests.patch(url, headers=self._headers(), json=data, timeout=self.timeout)
        if not response.ok:
            logger.error(f"Graph request failed: status={response.status_code} body={response.text}")
            logger.error(f"Headers: {response.headers}")
            return None
        else:
            return response

    def _delete(self, endpoint) -> requests.Response:
        """DELETE request to Microsoft Graph API."""
        url = f"{GRAPH_API_URL}{endpoint}"
        response = requests.delete(url, headers=self._headers(), timeout=self.timeout)
        response.raise_for_status()
        if not response.ok:
            logger.error(f"Graph request failed: status={response.status_code} body={response.text}")
            logger.error(f"Headers: {response.headers}")
            return None
        else:
            return response
    
    # ---------------------------
    # Office 365
    # ---------------------------
    
    def me(self) -> dict:
        """ get personal info of signed-in user

        Returns:
            dict: json output
        """
        resp : requests.Response = self._get("/me")
        if resp:
            return resp.json()
    
    def users(self) -> dict:
        """ retrieve the users related to this sign-in

        Returns:
            dict: json user output
        """
        resp : requests.Response = self._get("/users")
        if resp:
            return resp.json()
    
    # ---------------------------
    # Outlook Mail
    # ---------------------------        
    
    def me_messages(self) -> dict:
        """ get emails from signed-in user

        Returns:
            dict: json message output
        """
        resp : requests.Response = self._get("/me/messages")
        if resp:
            return resp.json()
        
    def me_sendmail(self, subject : str, body : str, recipients : list[str]) -> bool:
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
        resp : requests.Response = self._post("/me/sendmail", data)
        if resp:
            return True
        else:
            return False
    
    
    def send_mail(self, user_id : str, subject : str, body : str, recipients : list[str]) -> bool:
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
        resp : requests.Response = self._post(f"/users/{user_id}/sendMail", data)
        if resp:
            return True
        else:
            return False
    
    def get_messages(self, user_id : str, folder : str = None, select : str = "id, subject, from, receivedDateTime, bodyPreview", search : str = None, filter : str = None, top : int = 1000) -> dict:
        endpoint : str
        if folder:
            endpoint = f"/users/{user_id}/mailFolders/{folder}/messages"
        else:
            endpoint = f"/users/{user_id}/messages"
        if filter:
            params = {
                "$select": select,
                "$top": top,
                "$filter": filter
            }
        elif search:
            params = {
                "$select": select,
                "$top": top,
                "$search": f'"{search}"'
            }
        else:
            params = {
                "$select": select,
                "$top": top,
            }
        response : requests.Response = self._get(endpoint, params)
        if response:
            return response.json()
        else:
            return None
    
    # --------------------------------
    # Outlook Calendar
    # --------------------------------
    
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
        response : requests.Response = self._post(f"/users/{user_id}/calendars", data)
        if response:
            return response.json().get("id", None)
        else:
            return None
    
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
            resp : requests.Response = self._get(endpoint)
            if resp:
                data : dict = resp.json()

                for calendar in data.get("value", []):
                    if calendar["name"] == calendar_name:
                        return calendar["id"]

                # Handle pagination
                endpoint = data.get("@odata.nextLink").replace(GRAPH_API_URL, "")
            else:
                endpoint = None
            
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
        response : requests.Response = self._post(f"/users/{user_id}/calendars/{calendar_id}/events", data)
        if response:
            return response.json().get("id", None)
        else:
            return None
    
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
        response : requests.Response = self._get(f"/users/{user_id}/calendars/{calendar_id}/events", params)
        if response:
            return response.json().get("value", [])[0].get("id", None)
        else:
            return None
        
    
    def get_events_by_filter(self, user_id : str, calendar_id : str, filter : str) -> list[str]:
        params = {
            "$filter": filter
        }
        response : requests.Response = self._get(f"/users/{user_id}/calendars/{calendar_id}/events", params)
        if response:
            events = response.json().get("value", [])
            return [event["id"] for event in events]
        else:
            return None
    
    def get_all_calendar_events(self, user_id : str, calendar_id : str) -> list[str]:
        endpoint = f"/users/{user_id}/calendars/{calendar_id}/events?$select=id"
        event_ids : list[str] = []
        while endpoint:
            response : requests.Response = self._get(endpoint)
            if response:
                data : dict = response.json()                
                for event in data.get("value", []):
                    event_ids.append(event["id"])
                    
                endpoint = data.get("@odata.nextLink")
        return event_ids
    
    def delete_calendar_event(self, user_id : str, calendar_id : str, event_id : str) -> bool:
        response : requests.Response = self._delete(f"/users/{user_id}/calendars/{calendar_id}/events/{event_id}")
        if response:
            return True
        else:
            return False
    
    def update_calendar_event(self, user_id : str, calendar_id : str, event_id : str, subject : str = None, body : str = None, start : datetime = None, end : datetime = None, reminder_minutes_before_start : int = 0, tz_start : str = "Europe/Berlin", tz_end : str = "Europe/Berlin") -> bool:
        endpoint = f"/users/{user_id}/calendars/{calendar_id}/events/{event_id}"
        data : dict = {}
        if subject:
            data["subject"] = subject
        if body:
            data["body"] = {
                "contentType": "html",
                "content": body
            }
        if start:
            data["start"] = {
                "dateTime": start.strftime("%Y-%m-%dT%H:%M:%S.%f") + "0",
                "timeZone": tz_start
            }
        if end:
            data["end"] = {
                "dateTime": end.strftime("%Y-%m-%dT%H:%M:%S.%f") + "0",
                "timeZone": tz_end
            }
        if reminder_minutes_before_start > 0:
            data["reminderMinutesBeforeStart"] = reminder_minutes_before_start
            data["isReminderOn"] = True
        response : requests.Response = self._patch(endpoint, data)
        if response:
            return True
        else:
            return False
    
    # ----------------------------------------
    # SHAREPOINT
    # ----------------------------------------
    def get_sites(self, hostname : str) -> list[dict]:
        endpoint : str = "/sites/getAllSites"
        sites : list[str] = []
        while endpoint:
            response : requests.Response = self._get(endpoint)
            if response:
                data : dict = response.json()
                for site in data.get("value", []):
                    # Primary method: siteCollection.hostName
                    site_hostname = (
                        site.get("siteCollection", {})
                        .get("hostName")
                    )

                    # Fallback: hostname is also the first part
                    # of the Graph site ID.
                    if not site_hostname:
                        site_id = site.get("id", "")
                        site_hostname = site_id.split(",")[0]

                    if site_hostname.lower() == hostname.lower():
                        sites.append(site)

                # Graph pagination
                
                endpoint = data.get("@odata.nextLink", None)
                if endpoint:
                    endpoint = endpoint.replace(GRAPH_API_URL, "")
            else:
                endpoint = None

        return sites

    def get_site_by_name(self, hostname : str, name : str) -> str:
        sites : list[dict] = self.get_sites(hostname)
        if len(sites) > 0:
            for site in sites:
                if site["name"] == name:
                    return site["id"]
            return None
        else:
            return None
    
    def get_drive_ids(self, site_id) -> list[dict]:
        endpoint : str = f"/sites/{site_id}/drives"
        response : requests.Response = self._get(endpoint)
        if response:
            return response.json()["value"]
        else:
            return None   
    
    def get_drive_by_name(self, site_id, drive_name : str) -> str:
        pass
            
    # ----------------------------------------
    # ONEDRIVE
    # ----------------------------------------
       
    def get_file_info(self, user_id : str, onedrive_path : str) -> dict:
        endpoint : str =  f"/users/{user_id}/drive/root:/{onedrive_path}"
        response : requests.Response = self._get(endpoint)
        if response:
            return response.json()
        else:
            return None
    
    def get_file_content(self, user_id : str, onedrive_path : str, download_path : str) -> bool:
        endpoint : str =  f"/users/{user_id}/drive/root:/{onedrive_path}/:content"
        response : requests.Response = self._get(endpoint)
        if response:
            with open(download_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            return False    