from uuid import UUID

from blustorymicroservices.BluStoryOperators.models.dtos import \
    Operator, Member
from blustorymicroservices.BluStoryOperators.models.exceptions.members import MemberNotFoundException
from blustorymicroservices.BluStoryOperators.models.responses.api.members.CreatedMemberResponse import CreatedMemberResponse
from blustorymicroservices.BluStoryOperators.models.responses.api.members.MemberGenerateDeepLinkResponse import MemberGenerateDeepLinkResponse
from blustorymicroservices.BluStoryOperators.repository import \
    OperatorsRepository, MembersRepository

from blustorymicroservices.BluStoryOperators.settings.config import get_settings

class MemberService:
    def __init__(self, member_repo: MembersRepository, license_holder_repo: OperatorsRepository):
        self._member_repo = member_repo
        self._license_holder_repo = license_holder_repo
    def register_member(self,username: str,first_name:str,license_holder_id: UUID) -> CreatedMemberResponse:
        member = self._member_repo.create_member(username,first_name,license_holder_id)
        deep_link = self._member_repo.generate_setup_link(username)
        return CreatedMemberResponse(member=member,deep_link=deep_link)
    def get_member_by_id(self, license_holder_id: UUID, member_id: UUID) -> Member | None:
        return self._member_repo.get_member_by_id(license_holder_id, member_id)
    def get_members_by_license_holder(self, license_holder_id: UUID) -> list[Member]:
        return self._member_repo.get_members_by_license_holder(license_holder_id)
    def delete_member_by_id(self, license_holder_id: UUID,member_id: UUID) -> Member | None:
        return self._member_repo.delete_member_by_id(license_holder_id,member_id)
    def update_member_by_id(self, license_holder_id: UUID, member_id: UUID, new_username: str) -> Member | None:
        return self._member_repo.update_member_by_id(license_holder_id, member_id, new_username)
    def reset_member_pin(self, member_id: UUID) -> None:
        new_pin = self._member_repo.reset_member_pin(member_id)
        return new_pin
    def generate_member_deep_link(self,license_holder_id: UUID, member_id: UUID) -> MemberGenerateDeepLinkResponse:
        member = self._member_repo.get_member_by_id(license_holder_id, member_id)
        if member is None:
            raise MemberNotFoundException(member_id=str(member_id))
        deep_link = self._member_repo.generate_setup_link(member.username)
        return MemberGenerateDeepLinkResponse(deep_link=deep_link)
    
