from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.models.dtos import \
    LicenseHolder, Student
from blustorymicroservices.BluStoryLicenseHolders.models.exceptions.students import StudentNotFoundException
from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.students.CreatedStudentResponse import CreatedStudentResponse
from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.students.StudentGenerateDeepLinkResponse import StudentGenerateDeepLinkResponse
from blustorymicroservices.BluStoryLicenseHolders.repository import \
    LicenseHoldersRepository, StudentsRepository

from blustorymicroservices.BluStoryLicenseHolders.settings.config import get_settings

class StudentService:
    def __init__(self, student_repo: StudentsRepository, license_holder_repo: LicenseHoldersRepository):
        self._student_repo = student_repo
        self._license_holder_repo = license_holder_repo
    def register_student(self,username: str,first_name:str,license_holder_id: UUID) -> CreatedStudentResponse:
        student = self._student_repo.create_student(username,first_name,license_holder_id)
        deep_link = self._student_repo.generate_setup_link(username)
        return CreatedStudentResponse(student=student,deep_link=deep_link)
    def get_student_by_id(self, license_holder_id: UUID, student_id: UUID) -> Student | None:
        return self._student_repo.get_student_by_id(license_holder_id, student_id)
    def get_students_by_license_holder(self, license_holder_id: UUID) -> list[Student]:
        return self._student_repo.get_students_by_license_holder(license_holder_id)
    def delete_student_by_id(self, license_holder_id: UUID,student_id: UUID) -> Student | None:
        return self._student_repo.delete_student_by_id(license_holder_id,student_id)
    def update_student_by_id(self, license_holder_id: UUID, student_id: UUID, new_username: str) -> Student | None:
        return self._student_repo.update_student_by_id(license_holder_id, student_id, new_username)
    def reset_student_pin(self, student_id: UUID) -> None:
        new_pin = self._student_repo.reset_student_pin(student_id)
        return new_pin
    def generate_student_deep_link(self,license_holder_id: UUID, student_id: UUID) -> StudentGenerateDeepLinkResponse:
        student = self._student_repo.get_student_by_id(license_holder_id, student_id)
        if student is None:
            raise StudentNotFoundException(student_id=str(student_id))
        deep_link = self._student_repo.generate_setup_link(student.username)
        return StudentGenerateDeepLinkResponse(deep_link=deep_link)
    
