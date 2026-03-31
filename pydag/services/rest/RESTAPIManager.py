from enum import Enum
from typing import Optional

from fastapi import Depends, HTTPException, Header
from win32comext import authorization

class APIRole(int, Enum):
    ADMIN = "ADMIN"
    WRITE = "WRITE"
    READ = "READ"
    
ROLE_HIERARCHY = {
    APIRole.ADMIN: 3,
    APIRole.WRITE: 2,
    APIRole.READ: 1
}
    
class RESTAPIManager:
    
    def __init__(self):
        self._api_keys = {}  # Store API keys and their associated roles

    def generate_api_key(self, role: APIRole) -> str:
        """Generate a new API key for a given role."""
        import uuid
        api_key = str(uuid.uuid4())
        self._api_keys[api_key] = role
        return api_key

    def validate_api_key(self, api_key: str) -> bool:
        """Validate if the provided API key is valid."""
        return api_key in self._api_keys

    def get_api_key(self, authorization : Optional[str] = Header(default=None)) -> str:
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

    def get_role(self, api_key: str = Depends(get_api_key)) -> APIRole:
        for role, keys in self._api_keys.items():
            if api_key in keys:
                return APIRole(role)
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    def require_min_role(self, min_role: APIRole):
        def checker(role: APIRole = Depends(self.get_role)):
            if ROLE_HIERARCHY[role] < ROLE_HIERARCHY[min_role]:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return role
        return checker
    
    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key."""
        if api_key in self._api_keys:
            del self._api_keys[api_key]
            return True
        return False