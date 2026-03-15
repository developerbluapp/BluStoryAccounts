import random
import secrets
import string
from uuid import UUID

from blustorymicroservices.BluStoryOperators.clients.api.OrganisationClient import OrganisationClient
from blustorymicroservices.BluStoryOperators.helpers.OrganisationHelper import OrganisationHelper
from blustorymicroservices.BluStoryOperators.models.dtos import \
    Operator, Member
from blustorymicroservices.BluStoryOperators.models.responses.api.operators.CreatedOperatorResponse import CreatedOperatorResponse
from blustorymicroservices.BluStoryOperators.repository import \
    OperatorsRepository, MembersRepository
from blustorymicroservices.BluStoryOperators.settings.config import get_settings


class OperatorService:
    def __init__(self, operator_repo: OperatorsRepository, member_repo: MembersRepository, organisation_client: OrganisationClient):
        self._operator_repo = operator_repo
        self._member_repo = member_repo
        self._organisation_client = organisation_client

    def create_random_username(self,length: int = 10) -> str:
        settings = get_settings()
        alphabet = string.ascii_lowercase + string.digits
        return settings.operator.prefix + ''.join(secrets.choice(alphabet) for _ in range(length))

    def create_random_password(self,length: int = 20) -> str:
        if length < 8:
            raise ValueError("Password length should be at least 8")

        lowercase = secrets.choice(string.ascii_lowercase)
        uppercase = secrets.choice(string.ascii_uppercase)
        digit = secrets.choice(string.digits)
        symbol = secrets.choice("!@#$%^&*()-+")

        remaining_length = length - 4
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-+"

        remaining = [secrets.choice(alphabet) for _ in range(remaining_length)]

        password_list = [lowercase, uppercase, digit, symbol] + remaining

        random.SystemRandom().shuffle(password_list)

        return ''.join(password_list)
    def _build_email(self, username: str,organisation_name:str) -> str:
        organisation_name = OrganisationHelper.clean_organisation_name(organisation_name)
        return f"{username}.{organisation_name}{get_settings().email.suffix}"
    def register_operator(self, organisation_id: UUID) -> CreatedOperatorResponse:
        username = self.create_random_username()
        password = self.create_random_password()  # You'll need to implement this method
        organisation_data = self._organisation_client.get_organisation_name(organisation_id)
        fake_email = self._build_email(username, organisation_data.organisation_name)
        print(fake_email,"fake email in service")
        return self._operator_repo.create_operator(username, password, fake_email, organisation_data.organisation_name,organisation_id)

    def get_operator_by_id(self, operator_id: UUID) -> Operator | None:
        return self._operator_repo.get_operator_by_id(operator_id)
    def get_operators_by_organisation(self, organisation_id: UUID) -> list[Operator]:
        return self._operator_repo.get_operators_by_organisation(organisation_id)
