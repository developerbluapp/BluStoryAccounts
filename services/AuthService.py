import random
import secrets
import string
from pydantic import EmailStr
from uuid import UUID
from blustorymicroservices.BluStoryLicenseHolders.models.dtos import \
    AuthLicenseHolder, AuthLicenseHolder, LicenseHolder, Student
from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.licenseholders.LicenseHolderSessionReponse import LicenseHolderSessionResponse
from blustorymicroservices.BluStoryLicenseHolders.repository import \
    LicenseHoldersRepository, StudentsRepository


class AuthService:
    def __init__(self, license_holder_repo: LicenseHoldersRepository, student_repo: StudentsRepository):
        self._license_holder_repo = license_holder_repo
        self._student_repo = student_repo
    def create_random_username(self, length : int=20) -> str:
        alphabet = string.ascii_lowercase + string.digits  # 36 characters
        username = ''.join(secrets.choice(alphabet) for _ in range(length))
        return username
    def signup_license_holder(self, auth_license_holder_dto: AuthLicenseHolder) -> LicenseHolderSessionResponse:
        username = self.create_random_username()
        return self._license_holder_repo.signup_license_holder(auth_license_holder_dto,username)
    def signin_license_holder(self, auth_license_holder_dto: AuthLicenseHolder) -> LicenseHolderSessionResponse:
        return self._license_holder_repo.signin_license_holder(auth_license_holder_dto)