import random
import secrets
import string
from pydantic import EmailStr
from uuid import UUID
from blustorymicroservices.BluStoryAccounts.models.dtos import \
    AuthMember, MemberSession
from blustorymicroservices.BluStoryAccounts.models.dtos.MemberDeepLink import MemberDeepLink
from blustorymicroservices.BluStoryAccounts.repository import \
    OperatorsRepository, MembersRepository

class MemberAuthService:
    def __init__(self,member_repo: MembersRepository):
        self._member_repo = member_repo

    def signin_member(self, auth_member_dto: AuthMember) -> MemberSession:
        return self._member_repo.signin_member(auth_member_dto)
    def pin_signin_member(self, member_id: UUID, pin: str) -> MemberDeepLink:
        return self._member_repo.pin_signin_member(member_id, pin)