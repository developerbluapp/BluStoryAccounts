
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.blustory_accounts_auth.models.dtos import Member
class MemberSession(BaseModel):
    member: Member
    session: Session