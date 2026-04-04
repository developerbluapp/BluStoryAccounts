
from uuid import UUID

from pydantic import BaseModel

from blustorymicroservices.blustory_accounts_auth.models.dtos.Member import Member


class CreatedMemberResponse(BaseModel):
    member: Member
    deep_link: str


