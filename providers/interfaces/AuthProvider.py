# blustorymicroservices/BluStoryAccounts/repositories/interfaces.py
from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional,  Dict, Any
from gotrue.types import User, UserResponse,AuthResponse
from uuid import UUID

class AuthProvider(ABC):
    """Handles user identity & sessions (signup, signin, magic links, delete user, ...)"""

    @abstractmethod
    def create_user(
        self,
        email: str,
        password: str,
        email_confirm: bool = True,
        user_metadata: Optional[Dict] = None,
        app_metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:   # returns something with at least {"id": str}
        pass

    @abstractmethod
    def delete_user(self, user_id: str | UUID) -> None:
        pass

    @abstractmethod
    def generate_magic_link(
        self,
        email: str,
        redirect_to: Optional[str] = None,
    ) -> str:   # returns the action_link
        pass

    @abstractmethod
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        # should return something like {"access_token": ..., "user": {...}, ...}
        pass

    @abstractmethod
    def get_user_by_token(self, access_token: str) -> AuthResponse:
        pass
    @abstractmethod
    def get_user_by_id(self,id:UUID) -> Optional[UserResponse]:
        pass
