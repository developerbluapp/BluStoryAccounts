from pydantic import BaseModel
from uuid import UUID
class MemberDeepLink(BaseModel):
    member_id: UUID
    deep_link: str