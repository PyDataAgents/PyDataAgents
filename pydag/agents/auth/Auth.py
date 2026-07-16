from abc import abstractmethod
from datetime import datetime, timedelta
import enum
from pathlib import Path
from fastapi import Request
from nicegui import ui
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
import yaml
import secrets
from pwdlib import PasswordHash

class Roles(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"

class Authenticator:
    """ An abstract interface for user authentication. """
    
    @abstractmethod
    def verify_user(self, username : str, password : str) -> bool:
        """ Verify the provided username and password. Returns True if valid, False otherwise. """
    
    @abstractmethod
    def verify_token(self, token : str) -> bool:
        """ Verify the provided authentication token. Returns True if valid, False otherwise. """


class TokenManager:
    """
    Manager for JWT token management.
    """
    
    _instance = None
    _secret = secrets.token_hex(32)
    _algorithm = "HS256"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @staticmethod
    def create_token(user : dict) -> str:
        """
        Create a JWT token for the given user. 

        Args:
            user (dict): A dictionary containing user information.
        """
        payload = {
            "id": user["id"],
            "roles": user["roles"],
            "exp": datetime.now() + timedelta(hours=8)
        }

        return jwt.encode(payload, TokenManager._secret, algorithm=TokenManager._algorithm)

    @staticmethod
    def decode_token(token):
        return jwt.decode(token, TokenManager._secret, algorithms=[TokenManager._algorithm])
    
class AuthManager:
    
    _instance = None

    def __new__(cls, users_file: str | Path):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(users_file)
        return cls._instance

    def __init__(self, users_file: str | Path = None):
        if getattr(self, "_initialized", False):
            return
        self._password_hash = PasswordHash.recommended()
        if users_file is not None:
            self._users_file : Path = Path(users_file)
        if self._users_file is not None:
            data : dict
            if self._users_file.exists():
                data = yaml.safe_load(self._users_file.read_text(encoding="utf-8")) 
            else:
                data = {}.setdefault("users", {})          
            self._users : dict = data.get("users", {})
            self._initialized = True    

    def _save(self):
        data = {"users": self._users}
        self._users_file.write_text(
            yaml.safe_dump(data, sort_keys=False),
            encoding="utf-8",
        )

    def add_user(self, username: str, password: str, roles: list[str]):
        if username in self._users:
            raise ValueError(f"User '{username}' already exists.")

        self._users[username] = {
            "password": self._password_hash.hash(password),
            "roles": roles,
        }

        self._save()

    def delete_user(self, username: str):
        if username not in self._users:
            raise ValueError(f"Unknown user '{username}'.")

        del self._users[username]
        self._save()

    def change_password(self, username: str, password: str):
        if username not in self._users:
            raise ValueError(f"Unknown user '{username}'.")

        self._users[username]["password"] = self._password_hash.hash(password)
        self._save()

    def set_roles(self, username: str, roles: list[str]):
        if username not in self._users:
            raise ValueError(f"Unknown user '{username}'.")

        self._users[username]["roles"] = roles
        self._save()

    def list_users(self):
        for username, user in self._users.items():
            roles = ", ".join(user.get("roles", []))
            print(f"{username:20} [{roles}]")    

    def authenticate(self, username: str, password: str):
        user : dict = self._users.get(username)

        if user is None:
            return None

        if not self._password_hash.verify(password, user["password"]):
            return None

        return {
            "id": username,
            "roles": user.get("roles", []),
        }
        
class AuthenticationMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get("access_token")
        request.state.user = None
        if token:
            try:
                request.state.user = TokenManager.decode_token(token)
            except Exception:
                pass
        return await call_next(request)
