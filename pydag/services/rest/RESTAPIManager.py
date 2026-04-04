from __future__ import annotations
from enum import Enum
import os
from typing import TYPE_CHECKING
import secrets
import webbrowser
from bs4 import BeautifulSoup
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader


from ...utils.HTMLUtils import HTMLUtils

if TYPE_CHECKING:    
    from .RestService import RestService


class APIRole(str, Enum):
    ADMIN = "ADMIN"
    WRITE = "WRITE"
    READ = "READ"
    
    
class RESTAPIManager:
    
    API_KEYS : dict = {}  # Store API keys and their associated roles

    ROLE_HIERARCHY = {
        APIRole.ADMIN: 3,
        APIRole.WRITE: 2,
        APIRole.READ: 1
    }
    
    API_KEY_TEMPLATE = os.path.dirname(__file__) + os.sep + "API_KEY_TEMPLATE.html"
    
    REST_SERVICE : RestService = None
    
    @staticmethod
    def generate_api_keys(api_key_file : str = None, service : RestService = None):
        """Generate a API keys for this application and roles."""        
        RESTAPIManager.REST_SERVICE = service  # Set the REST_SERVICE reference for API key checks
        # check if api_key_file already exists and load existing keys if so
        if api_key_file and os.path.exists(api_key_file):
            soup = HTMLUtils.open_html_doc(api_key_file)
            for role in APIRole:
                element = soup.find(id=f"apiKey-{role.value.lower()}")
                if element and element.has_attr('value'):
                    RESTAPIManager.API_KEYS[role] = element['value']
        else:
            soup : BeautifulSoup = HTMLUtils.open_html_doc(RESTAPIManager.API_KEY_TEMPLATE)
            for role, hierarchy in RESTAPIManager.ROLE_HIERARCHY.items():
                key = secrets.token_hex(16)
                if role not in RESTAPIManager.API_KEYS:
                    RESTAPIManager.API_KEYS[role] = key
                    HTMLUtils.replace_value_by_id(soup, f"apiKey-{role.lower()}", key)
            if api_key_file:
                HTMLUtils.save_html_doc(soup, api_key_file)
            else:
                api_key_file = "API_KEYS.html"
                HTMLUtils.save_html_doc(soup, api_key_file)        
        abs_path = os.path.abspath(api_key_file)
        webbrowser.open(f"file://{abs_path}")
        

    @staticmethod
    def get_api_key(api_key: str = Security(APIKeyHeader(name="Authorization", auto_error=False))) -> str:
        """Get the role associated with the provided API key."""
        if not RESTAPIManager.REST_SERVICE:
            return None  # If API keys are not required, return None
        if not api_key:
           raise HTTPException(status_code=401, detail="Missing Authorization header")                
        return api_key

    @staticmethod
    def get_role(api_key: str = Depends(get_api_key)) -> APIRole:
        if not RESTAPIManager.REST_SERVICE:
            return APIRole.ADMIN  # If API keys are not required, treat all requests as ADMIN
        for role, key in RESTAPIManager.API_KEYS.items():
            if api_key == key:
                return APIRole(role)
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    @staticmethod   
    def require_min_role(min_role : APIRole):
        def checker(role: APIRole = Depends(RESTAPIManager.get_role)):
            if RESTAPIManager.ROLE_HIERARCHY[role] < RESTAPIManager.ROLE_HIERARCHY[min_role]:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return role
        return checker