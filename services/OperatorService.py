import random
import secrets
import string
from uuid import UUID

from blustorymicroservices.BluStoryAccounts.repository.OrganisationRepository import OrganisationRepository
from blustorymicroservices.BluStoryAccounts.clients.api.OrganisationClient import OrganisationClient
from blustorymicroservices.BluStoryAccounts.helpers.OrganisationHelper import OrganisationHelper
from blustorymicroservices.BluStoryAccounts.models.dtos import \
    Operator, Member
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.ResetOperatorPasswordResponse import ResetOperatorPasswordResponse
from blustorymicroservices.BluStoryAccounts.models.responses.api.operators.CreatedOperatorResponse import CreatedOperatorResponse
from blustorymicroservices.BluStoryAccounts.repository import \
    OperatorsRepository, MembersRepository
from blustorymicroservices.BluStoryAccounts.settings.config import get_settings
from blustorymicroservices.BluStoryAccounts.helpers.AuthHelper import AuthHelper

class OperatorService:
    def __init__(self, operator_repo: OperatorsRepository, member_repo: MembersRepository, organisation_repo : OrganisationRepository):
        self._operator_repo = operator_repo
        self._member_repo = member_repo
        self._organisation_repo = organisation_repo



    def _build_operator_email(self, username: str,organisation_name:str) -> str:
        organisation_name = OrganisationHelper.clean_organisation_name(organisation_name)
        return f"{username}.{organisation_name}{get_settings().email.suffix}"
    def register_operator(self, organisation_id: UUID) -> CreatedOperatorResponse:
        username = AuthHelper.create_random_username()
        password = AuthHelper.create_random_password()  # You'll need to implement this method
        organisation_data = self._organisation_repo.get_organisation_by_id(organisation_id)
        fake_email = self._build_operator_email(username, organisation_data.name)
        return self._operator_repo.create_operator(username, password, fake_email, organisation_data.name,organisation_id)
    def reset_password(self, organisation_id: UUID, operator_id: UUID) ->ResetOperatorPasswordResponse:
        new_password = AuthHelper.create_random_password()
        return self._operator_repo.reset_password(organisation_id, operator_id, new_password)
    def get_operator_by_id(self, operator_id: UUID) -> Operator | None:
        return self._operator_repo.get_operator_by_id(operator_id)
    def get_operators_by_organisation(self, organisation_id: UUID) -> list[Operator]:
        return self._operator_repo.get_operators_by_organisation(organisation_id)
    def get_operator_count(self, organisation_id: UUID) -> int:
        return self._operator_repo.count_operators_by_organisation(organisation_id)
