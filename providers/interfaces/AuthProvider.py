# blustorymicroservices/BluStoryAccounts/repositories/interfaces.py
from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional,  Dict, Any
from gotrue.types import User, UserResponse,AuthResponse
from uuid import UUID
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from uuid import UUID
from gotrue.types import UserResponse, AuthResponse

class AuthProvider(ABC):
    @abstractmethod
    def create_user(self, email: str, password: str, email_confirm: bool = True, 
                    user_metadata: Optional[Dict] = None, app_metadata: Optional[Dict] = None) -> UserResponse:
        pass

    @abstractmethod
    def delete_user(self, user_id: Union[str, UUID]) -> None:
        pass

    @abstractmethod
    def sign_in(self, email: str, password: str) -> AuthResponse:
        pass

    @abstractmethod
    def get_user_by_token(self, access_token: str) -> UserResponse:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: Union[str, UUID]) -> Optional[UserResponse]:
        pass

    @abstractmethod
    def generate_magic_link(self, email: str, redirect_to: Optional[str] = None) -> str:
        pass