import random
import secrets
import string
from pydantic import EmailStr
from uuid import UUID
from blustorymicroservices.BluStoryOperators.models.dtos import \
    AuthOrganisation, AuthOrganisation, Organisation, Member
from blustorymicroservices.BluStoryOperators.models.dtos import OrganisationSession
from blustorymicroservices.BluStoryOperators.repository import \
    OrganisationsRepository


class OrganisationAuthService:
    def __init__(self, organisation_repo: OrganisationsRepository):
        self._organisation_repo = organisation_repo

    def signup_organisation(self, auth_organisation_dto: AuthOrganisation) -> OrganisationSession:
        return self._organisation_repo.signup_organisation(auth_organisation_dto)
    def signin_organisation(self, auth_organisation_dto: AuthOrganisation) -> OrganisationSession:
        return self._organisation_repo.signin_organisation(auth_organisation_dto)