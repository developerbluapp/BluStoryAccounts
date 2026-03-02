from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.models.dtos import \
    LicenseHolder,Student
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

    def create_student(self, username: str, password: str, license_holder_id: UUID) -> Student:
        try:
            settings = get_settings()
            fake_email = f"{username}{settings.email.suffix}"
            response = self._client.auth.admin.create_user({
                "email": fake_email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"username": username},
                "app_metadata": {"role": settings.roles.student,
                                "license_holder_id": license_holder_id } 
            })
            self._client.table("students").insert({
            "id": str(response.user.id),
            "license_holder_id": str(license_holder_id),
            "username": username
            }).execute()
            return self._map_supabase_auth_user_to_student(SupabaseUserResponse(**response.user.model_dump()))
        except AuthApiError as e:
            raise UserAlreadyExistsException(username=username)
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