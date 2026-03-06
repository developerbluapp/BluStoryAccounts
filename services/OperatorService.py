from uuid import UUID

from blustorymicroservices.BluStoryOperators.models.dtos import \
    Operator, Member
from blustorymicroservices.BluStoryOperators.repository import \
    OperatorsRepository, MembersRepository


class OperatorService:
    def __init__(self, license_holder_repo: OperatorsRepository, member_repo: MembersRepository):
        self._license_holder_repo = license_holder_repo
        self._member_repo = member_repo
    def register_member(self, username: str, password: str, license_holder_id: UUID) -> Member:
        return self._member_repo.create_member(username, password, license_holder_id)
    def get_license_holder_by_id(self, license_holder_id: UUID) -> Operator | None:
        return self._license_holder_repo.get_license_holder_by_id(license_holder_id)
