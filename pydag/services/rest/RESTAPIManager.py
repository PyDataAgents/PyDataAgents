from enum import Enum
import os
from typing import Optional
import secrets
from bs4 import BeautifulSoup
from fastapi import Depends, HTTPException, Header
import webbrowser


from ...utils.HTMLUtils import HTMLUtils


class APIRole(str, Enum):
    ADMIN = "ADMIN"
    WRITE = "WRITE"
    READ = "READ"
    
    
class RESTAPIManager:
    
    _api_keys : dict = {}  # Store API keys and their associated roles

    _role_hierarchies = {
        APIRole.ADMIN: 3,
        APIRole.WRITE: 2,
        APIRole.READ: 1
    }
    
    API_KEY_TEMPLATE = os.path.dirname(__file__) + os.sep + "API_KEY_TEMPLATE.html"
    
    @staticmethod
    def generate_api_keys(api_key_file : str = None):
        """Generate a API keys for this application and roles."""        
        soup : BeautifulSoup = HTMLUtils.open_html_doc(RESTAPIManager.API_KEY_TEMPLATE)
        for role, hierarchy in RESTAPIManager._role_hierarchies.items():
            key = secrets.token_hex(16)
            if role not in RESTAPIManager._api_keys:
                RESTAPIManager._api_keys[role] = key
                HTMLUtils.replace_value_by_id(soup, f"apiKey-{role.lower()}", key)
        if api_key_file:
            HTMLUtils.save_html_doc(soup, api_key_file)
            abs_path = os.path.abspath(api_key_file)
        else:
            HTMLUtils.save_html_doc(soup, "API_KEYS.html")
            abs_path = os.path.abspath("API_KEYS.html")
        webbrowser.open(f"file://{abs_path}")
        

    @staticmethod
    def get_api_key(authorization : Optional[str] = Header(default=None)) -> str:
        """Get the role associated with the provided API key."""
        if not authorization:
           raise HTTPException(status_code=401, detail="Missing Authorization header")        
        try:
            scheme, key = authorization.split(" ")
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="Invalid Authorization format") from exc
        if scheme != "ApiKey":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
        return key

    @staticmethod
    def get_role(api_key: str = Depends(get_api_key)) -> APIRole:
        for role, keys in RESTAPIManager._api_keys.items():
            if api_key in keys:
                return APIRole(role)
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    @staticmethod   
    def require_min_role(min_role : APIRole):
        def checker(role: APIRole = Depends(RESTAPIManager.get_role)):
            if RESTAPIManager._role_hierarchies[role] < RESTAPIManager._role_hierarchies[min_role]:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return role
        return checker