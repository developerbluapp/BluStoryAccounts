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
    def __init__(self, operator_repo: OperatorsRepository, member_repo: MembersRepository):
        self._operator_repo = operator_repo
        self._member_repo = member_repo
    def create_random_username(self, length : int=20) -> str:
        alphabet = string.ascii_lowercase + string.digits  # 36 characters
        username = ''.join(secrets.choice(alphabet) for _ in range(length))
        return username

    def signup_operator(self, auth_operator_dto: AuthOperator) -> OperatorSession:
        #username = self.create_random_username()
        return self._operator_repo.signup_operator(auth_operator_dto)
    def signin_operator(self, auth_operator_dto: AuthOperator) -> OperatorSession:
        return self._operator_repo.signin_operator(auth_operator_dto)