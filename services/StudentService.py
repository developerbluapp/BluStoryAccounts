from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.models.dtos import \
    LicenseHolder, Student
from blustorymicroservices.BluStoryLicenseHolders.repository import \
    LicenseHoldersRepository, StudentsRepository


class StudentService:
    def __init__(self, student_repo: StudentsRepository, license_holder_repo: LicenseHoldersRepository):
        self._student_repo = student_repo
        self._license_holder_repo = license_holder_repo
    def register_student(self, username: str, password: str, license_holder_id: UUID) -> Student:
        return self._student_repo.create_student(username, password, license_holder_id)
    def get_student_by_id(self, license_holder_id: UUID, student_id: UUID) -> Student | None:
        return self._student_repo.get_student_by_id(license_holder_id, student_id)
    def get_students_by_license_holder(self, license_holder_id: UUID) -> list[Student]:
        return self._student_repo.get_students_by_license_holder(license_holder_id)
    def delete_student_by_id(self, license_holder_id: UUID,student_id: UUID) -> Student | None:
        return self._student_repo.delete_student_by_id(license_holder_id,student_id)
    def update_student_by_id(self, license_holder_id: UUID, student_id: UUID, new_username: str) -> Student | None:
        return self._student_repo.update_student_by_id(license_holder_id, student_id, new_username)
    
