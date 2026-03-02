from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.models.dtos import \
    LicenseHolder, Student
from blustorymicroservices.BluStoryLicenseHolders.repository.SupabaseUserRepository import \
    SupabaseUserRepository


class UserService:
    def __init__(self, user_repo: SupabaseUserRepository):
        self._user_repo = user_repo
    def register_student(self, username: str, password: str, license_holder_id: UUID) -> Student:
        return self._user_repo.create_student(username, password, license_holder_id)
    def get_student_by_id(self, license_holder_id: UUID, student_id: UUID) -> Student | None:
        return self._user_repo.get_student_by_id(license_holder_id, student_id)
    def get_students_by_license_holder(self, license_holder_id: UUID) -> list[Student]:
        return self._user_repo.get_students_by_license_holder(license_holder_id)
    def delete_student_by_id(self, license_holder_id: UUID,student_id: UUID) -> Student | None:
        return self._user_repo.delete_student_by_id(license_holder_id,student_id)
    def update_student_by_id(self, license_holder_id: UUID, student_id: UUID, new_username: str) -> Student | None:
        return self._user_repo.update_student_by_id(license_holder_id, student_id, new_username)
    
