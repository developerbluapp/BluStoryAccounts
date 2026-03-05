
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.BluStoryLicenseHolders.models.dtos import Member
class MemberSession(BaseModel):
    member: Member
    session: Session