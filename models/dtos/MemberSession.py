
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.BluStoryOperators.models.dtos import Member
class MemberSession(BaseModel):
    member: Member
    session: Session