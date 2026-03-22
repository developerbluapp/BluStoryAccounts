# blustorymicroservices/BluStoryAccounts/infrastructure/supabase.py

from typing import Any, Dict, Optional

from supabase import Client
from gotrue.errors import AuthApiError

from blustorymicroservices.BluStoryAccounts.models.exceptions.members import UserAlreadyExistsException
from uuid import UUID

from blustorymicroservices.BluStoryAccounts.providers.interfaces.AuthProvider import AuthProvider
from gotrue.types import Session, User, UserResponse,AuthResponse, User


class SupabaseAuthProvider(AuthProvider):
    def __init__(self, client: Client):
        self.client = client

    # ✅ CREATE USER
    def create_user(
        self,
        email: str,
        password: str,
        email_confirm: bool = True,
        user_metadata=None,
        app_metadata=None,
    ) -> Dict[str, Any]:
        try:
            resp = self.client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": email_confirm,
                "user_metadata": user_metadata or {},
                "app_metadata": app_metadata or {},
            })
            return {"id": str(resp.user.id), **resp.user.model_dump()}

        except AuthApiError as e:
            if "already been registered" in str(e):
                raise UserAlreadyExistsException(email=email)
            raise

    # ✅ DELETE USER
    def delete_user(self, user_id: str | UUID) -> None:
        self.client.auth.admin.delete_user(str(user_id))

    # ✅ SIGN IN (renamed to match repo)
    def sign_in(self, email: str, password: str) -> AuthResponse:
        resp = self.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if hasattr(resp, "error") and resp.error:
            raise ValueError(resp.error.message)

        return resp

    # ✅ GET USER BY TOKEN (renamed to match repo)
    def get_user_by_token(self, access_token: str) -> Dict[str, Any]:
        resp: AuthResponse = self.client.auth.get_user(access_token)
        return resp

    # ✅ GET USER BY ID (NEW)
    def get_user_by_id(self, user_id: str | UUID) -> Optional[UserResponse]:
        resp = self.client.auth.admin.get_user_by_id(str(user_id))

        if not resp or not resp.user:
            return None

        return resp

    # ✅ UPDATE USER (NEW → for password reset)
    def update_user(self, user_id: str | UUID, password: Optional[str] = None) -> Dict[str, Any]:
        attributes = {}

        if password:
            attributes["password"] = password

        resp = self.client.auth.admin.update_user_by_id(
            uid=str(user_id),
            attributes=attributes
        )

        return resp.user.model_dump()

    # ✅ MAGIC LINK (unchanged)
    def generate_magic_link(self, email: str, redirect_to: Optional[str] = None) -> str:
        options = {"redirect_to": redirect_to} if redirect_to else {}

        resp = self.client.auth.admin.generate_link({
            "type": "magiclink",
            "email": email,
            "options": options
        })

        return resp.properties.action_link
    
