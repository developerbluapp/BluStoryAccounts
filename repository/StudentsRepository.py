import hashlib
import hmac
from http.client import HTTPException
from uuid import UUID

from fastapi import HTTPException

from blustorymicroservices.BluStoryLicenseHolders.models.auth import UserRoles
from blustorymicroservices.BluStoryLicenseHolders.models.dtos import \
    AuthLicenseHolder, AuthStudent, LicenseHolder, LicenseHolderSession,Student, StudentSession
from blustorymicroservices.BluStoryLicenseHolders.models.dtos.StudentDeepLink import StudentDeepLink
from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.licenseholders import UserSignupAlreadyExistsException
from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.students import ResetPinResponse
from blustorymicroservices.BluStoryLicenseHolders.settings.config import \
    get_settings
from blustorymicroservices.BluStoryLicenseHolders.settings.Settings import \
    Settings
from blustorymicroservices.BluStoryLicenseHolders.models.responses import SupabaseUserResponse
from supabase import Client, create_client
from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.students import UserAlreadyExistsException
from gotrue.errors import AuthApiError
import secrets
import uuid
import bcrypt
class StudentsRepository:
    def __init__(self, client: Client):
        self._client = client
     
    def _map_supabase_auth_user_to_student(self, user: SupabaseUserResponse) -> Student:
        return Student(
            id=user.id,
            username=user.user_metadata["username"],

        )
    def _build_email(self, username: str) -> str:
        return f"{username}{get_settings().email.suffix}"
    

    def _generate_pin(self,length=4) -> str:
        # Generates a random numeric PIN e.g. "7392"
        return "".join([str(secrets.randbelow(10)) for _ in range(length)])
    def generate_setup_link(self, username: str) -> str:
        settings = get_settings()
        fake_email = self._build_email(username)

        link_response = self._client.auth.admin.generate_link({
            "type": "magiclink",
            "email": fake_email,
            "options": {
                "redirect_to": settings.deeplink.url
            }
        })

        return link_response.properties.action_link
    def _derive_password(self, plain_pin: str) -> str:
        secret = get_settings().pin.secret
        return hmac.new(
            secret.encode(),
            plain_pin.encode(),
            hashlib.sha256
        ).hexdigest()
    def create_student(self,username: str,first_name:str,license_holder_id: UUID) -> Student:
        
        try:
            # Auto-generate PIN instead of accepting one from request
            plain_pin = self._generate_pin(4)
            pin_hash = bcrypt.hashpw(plain_pin.encode(), bcrypt.gensalt()).decode()
            role_response = self._client.table("roles").select("*").eq("name", UserRoles.STUDENT).maybe_single().execute()
            fake_email = self._build_email(username)
            password = self._derive_password(plain_pin)
            response = self._client.auth.admin.create_user({
                "email": fake_email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"username": username, "first_name":first_name},
                "app_metadata": {"role": role_response.data["name"],
                                "license_holder_id": license_holder_id } 
            })
            self._client.table("students").insert({
            "id": str(response.user.id),
            "username": username,
            "first_name":first_name,
            "pin_hash": pin_hash,
            "license_holder_id": str(license_holder_id),
            }).execute()
            
            if not response:
                raise HTTPException(status_code=500, detail="Failed to insert student record")

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
    def signin_student(self, auth_student_dto: AuthStudent) -> StudentSession:
        try:
            session_response = self._client.auth.sign_in_with_password({
                "email": f"{auth_student_dto.username}{get_settings().email.suffix}",
                "password": auth_student_dto.password
            })
            if "error" in session_response and session_response["error"]:
                raise HTTPException(status_code=400, detail=session_response["error"]["message"])
            user_response = self._client.auth.get_user(session_response.session.access_token)
            student = self._map_supabase_auth_user_to_student(SupabaseUserResponse(**user_response.user.model_dump()))
            return StudentSession(student=student, session=session_response.session)
        except AuthApiError as e:
            raise HTTPException(status_code=400, detail=str(e))
    def reset_student_pin(self, student_id: UUID) -> ResetPinResponse:
        new_pin = self.generate_pin(4)
        pin_hash = bcrypt.hashpw(new_pin.encode(), bcrypt.gensalt()).decode()
        result = self._client.table("students").update({
            "pin_hash": pin_hash
        }).eq("id", str(student_id)).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Student not found")

        return ResetPinResponse(student_id=student_id, pin=new_pin)
    def pin_signin_student(self, student_id: UUID, pin: str) -> StudentDeepLink:
                # 1. Find student by tablet ID
        result = self._client.table("students").select(
            "id, username, pin_hash"
        ).eq("student_id", student_id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Tablet not registered")

        student = result.data

        # 2. Verify PIN
        is_valid = bcrypt.checkpw(
            pin.encode(),
            student["pin_hash"].encode()
        )
        if not is_valid:
            raise HTTPException(status_code=401, detail="Incorrect PIN")

        # 3. Generate a magic link session for the student
        email = self._build_email(student["username"])
        link_response = self._client.auth.admin.generate_link({
            "type": "magiclink",
            "email": email
        })
        return StudentDeepLink(student_id=student_id, deep_link=link_response.properties.action_link)