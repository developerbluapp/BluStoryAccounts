from uuid import UUID

from blustorymicroservices.BluStoryLicenseHolders.models.dtos import \
    AuthLicenseHolder, AuthLicenseHolder, LicenseHolder, Student
from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.LicenseHolderSessionReponse import LicenseHolderSessionResponse
from blustorymicroservices.BluStoryLicenseHolders.repository.SupabaseUserRepository import \
    SupabaseUserRepository


class AuthService:
    def __init__(self, user_repo: SupabaseUserRepository):
        self._user_repo = user_repo
    def signup_license_holder(self, auth_license_holder_dto: AuthLicenseHolder) -> LicenseHolderSessionResponse:
        return self._user_repo.signup_license_holder(auth_license_holder_dto)