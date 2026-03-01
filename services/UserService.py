from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.models.dtos import CreatedUser
from blustorymicroservices.BluStoryLicenseHolders.repository.SupabaseUserRepository import SupabaseUserRepository


class UserService:
    def __init__(self, user_repo: SupabaseUserRepository):
        self._user_repo = user_repo

    def register_user(self, username: str, password: str, license_holder_id: UUID) -> CreatedUser:
        return self._user_repo.create_user(username, password, license_holder_id)
    def get_students_by_license_holder(self, license_holder_id: str) -> list[CreatedUser]:
        return self._user_repo.get_students_by_license_holder(license_holder_id)
    
    
