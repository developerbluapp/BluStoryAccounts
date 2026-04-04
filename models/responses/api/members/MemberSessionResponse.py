
from pydantic import BaseModel
from gotrue.types import Session
from blustorymicroservices.blustory_accounts_auth.models.responses.api.members.MemberResponse import MemberResponse
class MemberSessionResponse(BaseModel):
    member: MemberResponse
    session: Session