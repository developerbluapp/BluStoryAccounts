from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.models.dtos import \
    LicenseHolder, Student
from blustorymicroservices.BluStoryLicenseHolders.repository import \
    LicenseHoldersRepository, StudentsRepository


class LicenseHolderService:
    def __init__(self, license_holder_repo: LicenseHoldersRepository, student_repo: StudentsRepository):
        self._license_holder_repo = license_holder_repo
        self._student_repo = student_repo
    def register_student(self, username: str, password: str, license_holder_id: UUID) -> Student:
        return self._student_repo.create_student(username, password, license_holder_id)
    def get_license_holder_by_id(self, license_holder_id: UUID) -> LicenseHolder | None:
        return self._license_holder_repo.get_license_holder_by_id(license_holder_id)
