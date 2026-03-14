from uuid import UUID

from blustorymicroservices.BluStoryOperators.models.dtos import \
    Operator, Member
from blustorymicroservices.BluStoryOperators.repository import \
    OperatorsRepository, MembersRepository


class OperatorService:
    def __init__(self, operator_repo: OperatorsRepository, member_repo: MembersRepository):
        self._operator_repo = operator_repo
        self._member_repo = member_repo
    def register_member(self, username: str, password: str, operator_id: UUID) -> Member:
        return self._member_repo.create_member(username, password, operator_id)
    def get_operator_by_id(self, operator_id: UUID) -> Operator | None:
        return self._operator_repo.get_operator_by_id(operator_id)
