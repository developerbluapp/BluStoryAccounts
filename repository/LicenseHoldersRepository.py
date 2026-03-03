from http.client import HTTPException
from urllib import response
from uuid import UUID

from fastapi import HTTPException

from blustorymicroservices.BluStoryLicenseHolders.models.auth import UserRoles
from blustorymicroservices.BluStoryLicenseHolders.models.dtos import \
    AuthLicenseHolder, LicenseHolder, LicenseHolderSession,Student
from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.licenseholders import UserSignupAlreadyExistsException
from blustorymicroservices.BluStoryLicenseHolders.settings.config import \
    get_settings
from blustorymicroservices.BluStoryLicenseHolders.settings.Settings import \
    Settings
from blustorymicroservices.BluStoryLicenseHolders.models.responses import SupabaseUserResponse
from supabase import Client, create_client
from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.licenseholders.LicenseHolderResponse import LicenseHolderResponse
from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.students import UserAlreadyExistsException
from gotrue.errors import AuthApiError
class LicenseHoldersRepository:
    def __init__(self, client: Client):
        self._client = client

    def _map_supabase_auth_user_to_license_holder(self, user: SupabaseUserResponse) -> LicenseHolder:
        return LicenseHolder(
            id=user.id,
            email=user.email,
            phone=user.phone,
            email_confirmed_at=user.email_confirmed_at,
            phone_confirmed_at=user.phone_confirmed_at,
            confirmed_at=user.confirmed_at,
            last_sign_in_at=user.last_sign_in_at,
            app_metadata=user.app_metadata,
            user_metadata=user.user_metadata,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_anonymous=user.is_anonymous
        )

    def signup_license_holder(self, auth_license_holder_dto: AuthLicenseHolder, username: str) -> LicenseHolderSession:
        try:
                # 1. Sign up user
            role_response = self._client.table("roles").select("*").eq("name", UserRoles.LICENSE_HOLDER).maybe_single().execute()
            response = self._client.auth.admin.create_user({
                "email": auth_license_holder_dto.email,
                "password": auth_license_holder_dto.password,
                "email_confirm": True,
                "user_metadata": {"username": username},
                "app_metadata": {"role": role_response.data["name"]} 
            })
                        # 2. Sign in the user to get a session
            session_response = self._client.auth.sign_in_with_password({
                "email": auth_license_holder_dto.email,
                "password": auth_license_holder_dto.password
            })
            if "error" in session_response and session_response["error"]:
                raise HTTPException(status_code=400, detail=session_response["error"]["message"])
            license_holder = self._map_supabase_auth_user_to_license_holder(SupabaseUserResponse(**response.user.model_dump()))
            return LicenseHolderSession(
                licenseholder=license_holder,
                session=session_response.session
            )
        except AuthApiError as e:
            if "already been registered" in str(e):
                raise UserSignupAlreadyExistsException(email=auth_license_holder_dto.email)
            else:
                raise
    def signin_license_holder(self, auth_license_holder_dto: AuthLicenseHolder) -> LicenseHolderSession:
        try:
            session_response = self._client.auth.sign_in_with_password({
                "email": auth_license_holder_dto.email,
                "password": auth_license_holder_dto.password
            })
            if "error" in session_response and session_response["error"]:
                raise HTTPException(status_code=400, detail=session_response["error"]["message"])
            user_response = self._client.auth.get_user(session_response.session.access_token)
            license_holder = self._map_supabase_auth_user_to_license_holder(SupabaseUserResponse(**user_response.user.model_dump()))
            return LicenseHolderSession(
                licenseholder=license_holder,
                session=session_response.session
            )
        except AuthApiError as e:
            raise HTTPException(status_code=400, detail=str(e))
    def get_license_holder_by_id(self, license_holder_id: UUID) -> LicenseHolder | None:
        response = self._client.auth.admin.get_user_by_id(str(license_holder_id))
        if not response.user:
            return None
        return self._map_supabase_auth_user_to_license_holder(SupabaseUserResponse(**response.user.model_dump()))