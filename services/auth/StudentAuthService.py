import random
import secrets
import string
from pydantic import EmailStr
from uuid import UUID
from blustorymicroservices.BluStoryLicenseHolders.models.dtos import \
    AuthStudent, StudentSession
from blustorymicroservices.BluStoryLicenseHolders.repository import \
    LicenseHoldersRepository, StudentsRepository

class StudentAuthService:
    def __init__(self,student_repo: StudentsRepository):
        self._student_repo = student_repo

    def signin_student(self, auth_student_dto: AuthStudent) -> StudentSession:
        return self._student_repo.signin_student(auth_student_dto)