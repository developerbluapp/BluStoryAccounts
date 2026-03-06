import random
import secrets
import string
from pydantic import EmailStr
from uuid import UUID
from blustorymicroservices.BluStoryOperators.models.dtos import \
    AuthOperator, AuthOperator, Operator, Member
from blustorymicroservices.BluStoryOperators.models.dtos import OperatorSession
from blustorymicroservices.BluStoryOperators.repository import \
    OperatorsRepository, MembersRepository


class OperatorAuthService:
    def __init__(self, license_holder_repo: OperatorsRepository, member_repo: MembersRepository):
        self._license_holder_repo = license_holder_repo
        self._member_repo = member_repo
    def create_random_username(self, length : int=20) -> str:
        alphabet = string.ascii_lowercase + string.digits  # 36 characters
        username = ''.join(secrets.choice(alphabet) for _ in range(length))
        return username

    def signup_license_holder(self, auth_license_holder_dto: AuthOperator) -> OperatorSession:
        username = self.create_random_username()
        return self._license_holder_repo.signup_license_holder(auth_license_holder_dto,username)
    def signin_license_holder(self, auth_license_holder_dto: AuthOperator) -> OperatorSession:
        return self._license_holder_repo.signin_license_holder(auth_license_holder_dto)