from http.client import HTTPException
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
from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.students import UserAlreadyExistsException
from gotrue.errors import AuthApiError
class SupabaseUserRepository:
    def __init__(self, client: Client):
        self._client = client
     
    def _map_supabase_auth_user_to_student(self, user: SupabaseUserResponse) -> Student:
        return Student(
            id=user.id,
            username=user.user_metadata["username"],
        )
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

    def create_student(self, username: str, password: str, license_holder_id: UUID) -> Student:
        try:
            settings = get_settings()
            role_response = self._client.table("roles").select("*").eq("name", UserRoles.LICENSE_HOLDER).maybe_single().execute()
            fake_email = f"{username}{settings.email.suffix}"
            response = self._client.auth.admin.create_user({
                "email": fake_email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"username": username},
                "app_metadata": {"role": role_response.data["name"],
                                "license_holder_id": license_holder_id } 
            })
            self._client.table("students").insert({
            "id": str(response.user.id),
            "license_holder_id": str(license_holder_id),
            "username": username
            }).execute()
            return self._map_supabase_auth_user_to_student(SupabaseUserResponse(**response.user.model_dump()))
        except AuthApiError as e:
            if "already been registered" in str(e):
                raise UserAlreadyExistsException(username=username)
            else:
                raise
    def get_students_by_license_holder(self, license_holder_id: UUID) -> list[Student]:
        response = self._client.table("students")\
            .select("*")\
            .eq("license_holder_id", str(license_holder_id))\
            .execute()
        return [Student(**s) for s in response.data]

    def get_student_by_id(self, license_holder_id: UUID, student_id: UUID) -> Student | None:
        response = self._client.table("students")\
            .select("*")\
            .eq("license_holder_id", str(license_holder_id))\
            .eq("id", str(student_id))\
            .maybe_single()\
            .execute()
        return Student(id=response.data["id"], username=response.data["username"]) if response.data else None


    def delete_student_by_id(self, license_holder_id: UUID, student_id: UUID) -> Student | None:
        student = self.get_student_by_id(license_holder_id,student_id)
        if not student:
            return None
        self._client.auth.admin.delete_user(student.id)
        self._client.table("students").delete().eq("id", str(student.id)).execute()
        return student  # return what was deleted so caller can confirm
    def update_student_by_id(self, license_holder_id: UUID, student_id: UUID, new_username: str) -> Student | None:
        student = self.get_student_by_id(license_holder_id, student_id)
        if not student:
            return None
        self._client.table("students").update({"username": new_username}).eq("license_holder_id", str(license_holder_id)).eq("id", str(student.id)).execute()
        return Student(id=student.id, username=new_username)
    def signup_license_holder(self, auth_license_holder_dto: AuthLicenseHolder) -> LicenseHolderSession:
        try:
                # 1. Sign up user
            role_response = self._client.table("roles").select("*").eq("name", UserRoles.LICENSE_HOLDER).maybe_single().execute()
            response = self._client.auth.admin.create_user({
                "email": auth_license_holder_dto.email,
                "password": auth_license_holder_dto.password,
                "email_confirm": True,
                "app_metadata": {"role": role_response.data["name"]} 
            })
                        # 2. Sign in the user to get a session
            session_response = self._client.auth.sign_in_with_password({
                "email": auth_license_holder_dto.email,
                "password": auth_license_holder_dto.password
            })
            if "error" in session_response and session_response["error"]:
                raise HTTPException(status_code=400, detail=session_response["error"]["message"])

            return LicenseHolderSession(
                licenseholder=self._map_supabase_auth_user_to_license_holder(SupabaseUserResponse(**response.user.model_dump())),
                session=session_response.session
            )
        except AuthApiError as e:
            if "already been registered" in str(e):
                raise UserSignupAlreadyExistsException(email=auth_license_holder_dto.email)
            else:
                raise