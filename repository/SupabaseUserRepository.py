from uuid import UUID

from supabase import create_client, Client
from blustorymicroservices.BluStoryLicenseHolders.models.dtos import CreatedUser
from blustorymicroservices.BluStoryLicenseHolders.settings.Settings import Settings
from blustorymicroservices.BluStoryLicenseHolders.settings.config import get_settings

class SupabaseUserRepository:
    def __init__(self, client: Client):
        self._client = client

    def create_user(self, username: str, password: str, license_holder_id: UUID) -> CreatedUser:
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
        "id": response.user.id,
        "license_holder_id": license_holder_id,
        "username": username
        }).execute()
        return CreatedUser(id=response.user.id, email=response.user.email)
    def get_students_by_license_holder(self, license_holder_id: str) -> list[CreatedUser]:
        response = self._client.table("students")\
            .select("*")\
            .eq("license_holder_id", license_holder_id)\
            .execute()
        return [CreatedUser(id=s["id"], email=s["username"]) for s in response.data]