# blustorymicroservices/BluStoryAccounts/infrastructure/supabase.py

from typing import Any, Dict, Optional, Union

from supabase import Client
from gotrue.errors import AuthApiError

from blustorymicroservices.blustory_accounts_auth.models.exceptions.members import UserAlreadyExistsException
from uuid import UUID

from blustorymicroservices.blustory_accounts_auth.interfaces.AuthProvider import AuthProvider
from gotrue.types import Session, User, UserResponse,AuthResponse, User

class SupabaseAuthProvider(AuthProvider):
    def __init__(self, client: Client):
        self.client = client

    def create_user(self, email: str, password: str, **kwargs) -> UserResponse:
        # Supabase admin.create_user returns UserResponse
        return self.client.auth.admin.create_user({
            "email": email, "password": password, **kwargs
        })

    def delete_user(self, user_id: Union[str, UUID]) -> None:
        self.client.auth.admin.delete_user(str(user_id))

    def sign_in(self, email: str, password: str) -> AuthResponse:
        return self.client.auth.sign_in_with_password({"email": email, "password": password})

    def get_user_by_token(self, access_token: str) -> UserResponse:
        return self.client.auth.get_user(access_token)

    def get_user_by_id(self, user_id: Union[str, UUID]) -> Optional[UserResponse]:
        return self.client.auth.admin.get_user_by_id(str(user_id))

    def generate_magic_link(self, email: str, redirect_to: Optional[str] = None) -> str:
        resp = self.client.auth.admin.generate_link({
            "type": "magiclink", "email": email, 
            "options": {"redirect_to": redirect_to} if redirect_to else {}
        })
        return resp.properties.action_link