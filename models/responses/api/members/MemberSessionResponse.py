
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.BluStoryLicenseHolders.models.responses.api.members.MemberResponse import MemberResponse
class MemberSessionResponse(BaseModel):
    member: MemberResponse
    session: Session